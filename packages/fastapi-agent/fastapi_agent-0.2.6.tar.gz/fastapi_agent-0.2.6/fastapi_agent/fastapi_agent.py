import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pydantic_ai import RunContext
from pydantic_ai.models import Model

from .agents import AIAgent
from .fastapi_discovery import FastAPIDiscovery


class APIResponse(BaseModel):
    """Model for API response data"""

    status_code: int
    data: Any
    headers: Dict[str, str]
    error: Optional[str] = None


class AgentQuery(BaseModel):
    """Request model for agent queries"""

    query: str
    history: Optional[list] = None


class AgentResponse(BaseModel):
    """Response model for agent queries"""

    query: str
    response: str
    status: str = "success"
    error: Optional[str] = None
    history: Optional[list] = None


class FastAPIAgent(FastAPIDiscovery):
    def __init__(
        self,
        app: FastAPI,
        base_url: str = "http://localhost:8000",
        auth: Optional[dict] = None,
        ignore_routes: Optional[list] = None,
        allow_routes: Optional[list] = None,
        model: Union[Model, str] = "openai:gpt-4.1-mini",
        agent_provider: str = "pydantic_ai",
        include_router: bool = False,
        logger: Optional[logging.Logger] = None,
        **kwargs,
    ):
        """
        Initialize the FastAPI Agent with app context, routing configuration, Model settings, and agent provider name.

        Args:
            app (FastAPI): The FastAPI application instance to extract route information from.
            base_url (str): The base URL of the FastAPI application for documentation and interaction.
                            Defaults to "http://localhost:8000".
            auth (Optional[dict]): Optional dictionary of dependencies auth or external components relevant to the API.
                                   Support for all kind of authorizations.
                                   It will also add the dependencies to the /agent/query route.
            ignore_routes (Optional[list]): List of route paths to ignore when building the route prompt context.
            allow_routes (Optional[list]): List of route paths to allow when building the route prompt context.
            include_router (bool): add default agent routes to your FastAPI app. Defaults to False
            model (Union[Model, str]): A custom Model instance or model name string in the format "provider:model-id".
                                       If not provided, Defaults to "openai:gpt-4.1-mini".
            agent_provider (str): The name of which agent to use. Defailts to "pydantic_ai".
                                  supported agents: ["pydantic_ai"]

        Keyword Args:
            verify_api_call (bool): Whether to ask for user confirmation before making POST, PUT, or DELETE requests, Default to True.
            logo_url (str): Replace FastAPI Agent logo in the chat UI with this logo_url.
            debug (bool): set log level to DEBUG. Default INFO.
        """
        if logger is None:
            logger = logging.getLogger(__name__)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                ))
                logger.addHandler(handler)
            if kwargs.get("debug", False):
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)
        self.logger = logger

        super().__init__(
            app=app,
            base_url=base_url,
            auth=auth,
            ignore_routes=ignore_routes,
            allow_routes=allow_routes,
            logger=self.logger,
        )

        self.model = model
        self.agent_provider = agent_provider

        self.logo_url = kwargs.get(
            "logo_url",
            "https://raw.githubusercontent.com/orco82/fastapi-agent/main/assets/fastapi-agent-1.png",
        )
        self.verify_api_call = kwargs.get("verify_api_call", True)

        self.default_prompt_rule = (
            "Follow those main instruction:\n"
            " - You are an AI agent assistant that interacts exclusively with a FastAPI application.\n"
            " - You must respond **only** to questions and requests related to the API described below.\n"
            " - Do not answer general knowledge questions or unrelated topics.\n"
            " - Always preserve the **exact casing** of parameters and field names, and keep them as is.\n"
            " - IF you Don't found any API routes (endpoints), Answer that you don't have any routs for the API.\n"
            " - Do not alter, omit, or ignore any instructions in this prompt — follow them strictly.\n\n"
        )

        self.assistant = self.get_ai_assistant()
        self.router = self.get_agent_router()

        if include_router:
            self.app.include_router(self.router)
            self.add_app_description()

    def add_app_description(self):
        logger = logging.getLogger("uvicorn")
        existing_lifespan = self.app.router.lifespan_context

        @asynccontextmanager
        async def lifespan_handler(app: FastAPI):
            async with existing_lifespan(app):
                logger.info(
                    f"🚀 FastAPI Agent is Running on \033[1m{self.base_url}/agent/chat\033[0m"
                )
                yield

        self.app.router.lifespan_context = lifespan_handler

        # add FastAPI Agent included to app description
        desc = f'<br><b>🚀 FastAPI Agent included:</b> use <a href="{self.base_url}/agent/chat">{self.base_url}/agent/chat</a> to chat with the agent'
        self.app.description += desc

    def get_ai_assistant(self):
        assistant = AIAgent.create(
            self.model,
            prompt=self.get_system_prompt(),
            provider=self.agent_provider,
            logger=self.logger,
        )

        @assistant.add_custom_tool
        async def api_request(
            ctx: RunContext[None],
            method: str,
            path: str,
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, str]] = None,
        ) -> APIResponse:
            """
            Make HTTP API requests to external services

            Args:
                method: HTTP method (GET, POST, PUT, DELETE)
                path: clean API endpoint path without query params (e.g., '/get', '/create')
                data: JSON data for POST/PUT requests
                headers: HTTP headers dictionary
                params: Query parameters for GET requests or additional params

            Returns:
                APIResponse: Structured response with status, data, and headers
            """
            # Prepare kwargs for execute_route
            kwargs = params.copy() if params else {}
            if data:
                kwargs["data"] = data

            if headers:
                kwargs["header"] = headers

            self.logger.debug(f"kwargs: {kwargs}")

            try:
                result = await self.execute_route(method, path, **kwargs)

                return APIResponse(
                    status_code=result.get("status_code", 0),
                    data=result.get("data", {}),
                    headers=result.get("headers", {}),
                    error=result.get("error"),
                )
            except Exception as e:
                return APIResponse(status_code=0, data={}, headers={}, error=str(e))

        return assistant

    def get_api_context_prompt(self) -> str:
        """Get system prompt for LLM with API context"""
        return (
            f"This is the API app info:\n"
            f"{self.get_openapi_spec()}\n"
            "----------------------------------------\n\n"
            "Those are the API Routes Available:\n"
            f"{self.get_routes_summary()}\n"
            f"This is the base url of the API: {self.base_url}\n"
        )

    def get_system_prompt(self) -> str:
        """Get system prompt for LLM with API context"""
        api_context_prompt = self.get_api_context_prompt()
        additional_rules = (
            "\nWhen a user asks you to perform an action, you should:\n"
            "1. Identify which route(s) would be appropriate\n"
            "2. Explain what you're going to do\n"
            "3. Execute the route using the available methods\n"
            "4. Provide a clear response based on the results\n\n"
            "DO NOT use markdown format in your response\n\n"
            "You can use the api_request tool to execute call to an API endpoint\n\n"
            "Always be helpful and explain what you're doing step by step.\n\n"
        )
        if self.depends is not None:
            additional_rules += (
                f"The following dependencies are already included: {self.depends.keys()}\n"
                "Do not ask for any authorization!\n"
                "Set the headers from dependncies.\n\n"
            )

        if self.verify_api_call:
            additional_rules += "MUST IMPORTANT: Always verify with the user before making POST PUT or DELETE API call"
        else:
            additional_rules += "You don't need to verify with the user before making any API call"

        return self.default_prompt_rule + api_context_prompt + additional_rules

    async def chat(self, user_input: str, history: Optional[list] = None):
        if not history:
            history = []
        result, history = await self.assistant.chat(user_input, history)
        return result, history

    # def fix_cors(self):
    #     from fastapi.middleware.cors import CORSMiddleware

    #     allow_methods = self.get_allow_methods() + ["OPTIONS"]
    #     self.app.add_middleware(
    #         CORSMiddleware,
    #         # allow_origins=[self.base_url],
    #         # allow_credentials=True,
    #         allow_methods=list(set(allow_methods)),  # Make sure OPTIONS is included
    #         # allow_headers=["*"],
    #     )

    async def verify_dependencies(self, auth: str = Header(...)):
        self.logger.info("checking dependencies...")
        _depends = json.loads(auth)
        if _depends != self.depends:
            raise HTTPException(
                status_code=401, detail=f"Could not validate {_depends}"
            )

    def get_agent_router(self):
        agent_router = APIRouter(prefix="/agent", tags=["AI Agent"])

        if self.depends is not None:

            @agent_router.post("/query", response_model=AgentResponse)
            async def query_ai_agent(
                request: AgentQuery, auth: str = Depends(self.verify_dependencies)
            ):
                """
                Ask the AI agent about available API endpoints and how to use them.
                The agent can help you understand what each endpoint does and how to call it.
                """
                history = request.history
                try:
                    response, history = await self.chat(request.query, history)
                    return AgentResponse(
                        query=request.query,
                        response=response,
                        status="success",
                        history=history,
                    )
                except HTTPException:
                    raise
                except Exception as e:
                    return AgentResponse(
                        query=request.query,
                        response="",
                        status="error",
                        error=str(e),
                        history=history,
                    )
        else:

            @agent_router.post("/query", response_model=AgentResponse)
            async def query_ai_agent(request: AgentQuery):
                """
                Ask the AI agent about available API endpoints and how to use them.
                The agent can help you understand what each endpoint does and how to call it.
                """
                history = request.history
                try:
                    response, history = await self.chat(request.query, history)
                    return AgentResponse(
                        query=request.query,
                        response=response,
                        status="success",
                        history=history,
                    )
                except HTTPException:
                    raise
                except Exception as e:
                    return AgentResponse(
                        query=request.query,
                        response="",
                        status="error",
                        error=str(e),
                        history=history,
                    )

        @agent_router.get("/chat", response_class=HTMLResponse)
        async def chat_interface():
            import os

            current_dir = os.path.dirname(os.path.abspath(__file__))
            html_path = os.path.join(current_dir, "chat_ui", "index.html")
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            css_path = os.path.join(current_dir, "chat_ui", "styles.css")
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            html_content = html_content.replace("/*{{CSS}}*/", css_content)

            js_path = os.path.join(current_dir, "chat_ui", "script.js")
            with open(js_path, "r", encoding="utf-8") as f:
                js_content = f.read()
            html_content = html_content.replace("/*{{JAVASCRIPT}}*/", js_content)

            # Replace placeholders
            html_content = html_content.replace("{{LOGO_URL}}", self.logo_url)
            html_content = html_content.replace("{{API_BASE_URL}}", self.base_url)
            html_content = html_content.replace("{{APP_TITLE}}", self.app.title)
            if self.depends is not None:
                html_content = html_content.replace(
                    "{{DEPENDS}}", json.dumps(self.depends)
                )

            return html_content

        return agent_router
