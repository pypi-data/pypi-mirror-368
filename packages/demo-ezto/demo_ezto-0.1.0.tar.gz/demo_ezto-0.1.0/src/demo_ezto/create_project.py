import os
import subprocess

def create_fastapi_project():
    # Check if current directory is empty (to avoid overwriting)
    if os.listdir():
        confirm = input("Current directory is not empty. Proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return

    # Create directories
    os.makedirs("app/models", exist_ok=True)
    os.makedirs("app/repository", exist_ok=True)
    os.makedirs("app/routes", exist_ok=True)
    os.makedirs("app/services", exist_ok=True)
    os.makedirs("app/utils", exist_ok=True)
    os.makedirs("middleware", exist_ok=True)

    # Create empty __init__.py in each subfolder for Python packages
    open("app/__init__.py", "w").close()
    open("app/models/__init__.py", "w").close()
    open("app/repository/__init__.py", "w").close()
    open("app/routes/__init__.py", "w").close()
    open("app/services/__init__.py", "w").close()
    open("app/utils/__init__.py", "w").close()
    open("middleware/__init__.py", "w").close()

    # Write sample code to files (using your provided samples; adapted to filenames)
    # models/voice_model.py
    models_code = """from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class VoiceRequest(BaseModel):
    system_prompt: Optional[str] = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide the LLM response",
    )
    llm_call_required: bool = Field(
        default=True, description="Whether to process text through LLM before TTS"
    )
    text: str
    provider: Optional[str] = Field(
        default="edge_tts", description="TTS provider: 'gtts' or 'edge_tts'"
    )
    voice: Optional[str] = Field(
        default="en-US-GuyNeural", description="Voice id (only for edge_tts)"
    )
    speech_rate: Optional[str] = Field(
        default="+50%", description="Speech rate -100% to +100% (only for edge_tts)"
    )

    @field_validator("voice", "speech_rate")
    @classmethod
    def validate_edge_tts_params(cls, v, info):
        # Use info.data instead of values
        if info.data.get("provider") == "gtts" and v is not None:
            raise ValueError(
                f"'voice' and 'speech_rate' parameters are only supported with edge_tts provider"
            )
        return v


class VoiceResponse(BaseModel):
    audio_bytes: str
    response_text: str


class VoiceMetadataMessage(BaseModel):
    \"\"\"Model for audio metadata messages sent via WebSocket text\"\"\"

    agent_id: Optional[str] = Field(default=None, description="Project ID")
    language: str = Field(default="en", description="Language code")


class VoiceKnowledgeMessage(BaseModel):
    \"\"\"Model for knowledge base IDs sent via WebSocket text\"\"\"

    knowledge_base_ids: Optional[list[str]] = Field(
        default=None, description="List of knowledge base IDs associated with the audio"
    )
"""
    with open("app/models/voice_model.py", "w") as f:
        f.write(models_code)

    # repository/user_repository.py
    repository_code = """from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import delete, select
from app.models.api_models.user_model import UserRequestModel, UserModel
from app.models.db_models.user_model import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create_user(self, payload: UserModel) -> User:
        new_user = User(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            email=payload.email
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def is_email_available(self, email: str) -> bool:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return user is not None

    async def delete_user_by_id(self, user_id: str) -> bool:
        try:
            result = await self.session.execute(delete(User).where(User.id == user_id))
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.session.rollback()
            return False

    async def get_user_id_with_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
"""
    with open("app/repository/user_repository.py", "w") as f:
        f.write(repository_code)

    # routes/voice_routes.py
    routes_code = """import base64
import logging, asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.utils.constants import API_VERSION
from app.services.old_call_service.call_service import CallService as OldCallService, voice_service
from app.core.connection_manager import connection_manager

from app.core.websocket_manager import WebsocketManager
from app.services.call_service.call_service import CallService
from app.services.call_service.call_session_service import CallSessionService
from app.models.session.state_model import StateModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"/{API_VERSION}/voice", tags=["Voice"])

websocket_manager = WebsocketManager()
call_session_service = CallSessionService()
call_service = CallService()


@router.websocket("/call")
async def stream_synthetic_voice(
    websocket: WebSocket, audio_service: OldCallService = Depends(lambda: voice_service)
):
    \"\"\"Handle WebSocket voice call connections\"\"\"
    connection = None
    try:
        # Connect WebSocket
        connection = await connection_manager.connect(websocket)
        logger.info("WebSocket connected successfully")

        # Initialize voice service session
        voice_service_result = await audio_service.connect(
            websocket_connection=connection
        )

        if not voice_service_result:
            logger.error("Failed to connect voice service")
            await connection.close()
            return

        logger.info("Voice service connected, starting audio processing...")

        # Start receiving audio - this handles the entire session
        await audio_service.receive_audio_or_typescript(websocket_connection=connection)

    except WebSocketDisconnect as e:
        logger.info(f"WebSocket disconnected: {e}")
    except Exception as e:
        logger.error(f"Error in voice call: {str(e)}")
    finally:
        # Clean up connections
        if connection:
            logger.info("Cleaning up voice call connection")
            audio_service.disconnect(websocket_connection=connection)
            connection_manager.disconnect(connection)


@router.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    session_id = await websocket_manager.connect(websocket)
    try:
        # Wait for initial message with project_id (with timeout)
        try:
            initial_data = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        except asyncio.TimeoutError:
            await websocket.send_json(
                StateModel(
                    type="error",
                    text="Timeout waiting for init message with project_id",
                ).model_dump_json()
            )
            await websocket_manager.disconnect(session_id)
            return

        if initial_data.get("type") != "init" or "project_id" not in initial_data:
            await websocket.send_json(
                StateModel(
                    type="error", text="Expected init message with project_id"
                ).model_dump_json()
            )
            await websocket_manager.disconnect(session_id)
            return

        project_id = initial_data["project_id"]
        if not isinstance(project_id, str) or not project_id:
            await websocket.send_json(
                StateModel(
                    type="error", text="Invalid project_id: must be a non-empty string"
                ).model_dump_json()
            )
            await websocket_manager.disconnect(session_id)
            return

        # Create session with project_id
        await call_service.init_session(websocket, project_id)

        while True:
            try:
                data = await websocket.receive_bytes()
                await call_service.process_audio(data, websocket)
            except Exception as e:
                logger.error(
                    f"Error processing audio for client {session_id}: {str(e)}"
                )
                await websocket.send_json(
                    StateModel(type="error", text=f"{str(e)}").model_dump_json()
                )
    except WebSocketDisconnect:
        logger.info(f"Client {session_id} disconnected")
    except Exception as e:
        logger.error(f"Unexpected error for client {session_id}: {str(e)}")
        try:
            await websocket.send_json(
                StateModel(
                    type="error", text=f"Unexpected error: {str(e)}"
                ).model_dump_json()
            )
        except Exception:
            pass
    finally:
        await websocket_manager.disconnect(session_id)
        await call_session_service.remove_session(session_id)
"""
    with open("app/routes/voice_routes.py", "w") as f:
        f.write(routes_code)

    # services/voice_processor.py
    services_code = """import logging, time
from typing import Optional, Tuple, List, Dict
from app.core.environment import env
from app.services.speech_to_text_service import speech_to_text_service
from app.services.text_to_speech import text_to_speech_service
from app.services.llm_service import LLMService
from app.utils.constants import REPEATIATION_CHECK_REQUIRED
from app.models.api_models.voice_model import VoiceMetadataMessage
from app.services.api_services.knowledgebase_service import KnowledgeBaseService
from app.services.benchmark_service import timings, generate_benchmark_report
from app.models.session.project_model import SessionProject
from app.models.session.state_model import Conversation


logger = logging.getLogger(__name__)


class VoiceProcessor:
    \"\"\"Handles the complete audio processing pipeline\"\"\"

    def __init__(self):
        self.speech_to_text_service = speech_to_text_service
        self.llm_service = LLMService(system_prompt=env.VOICE_AI_LLM_SYSTEM_PROMPT)
        self.tts_service = text_to_speech_service

    def _is_repetitive_transcript(self, transcript: str) -> bool:
        \"\"\"Check if transcript contains repetitive content\"\"\"
        words = transcript.split()
        if len(words) <= 10:
            return False

        # Count most common word
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        max_count = max(word_counts.values())
        repetition_ratio = max_count / len(words)

        if repetition_ratio > 0.3:  # If any word is >30% of transcript
            logger.warning(f"Repetitive transcript detected: {repetition_ratio:.2%}")
            return True

        return False

    async def process_audio(
        self,
        audio_data: bytes,
        project: SessionProject,
        conversation_history: Optional[List[Conversation]] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[bytes]]:
        \"\"\"
        Process audio through the complete pipeline: STT -> RAG -> LLM -> TTS

        Returns:
            Tuple of (transcript, response, audio_response)
        \"\"\"
        try:

            language = 'ar' if project.language == "ARABIC" else 'en'  

            # Step 1: Speech-to-Text
            transcript = self.speech_to_text_service.transcribe_audio(
                audio_data, language=language
            )

            if not transcript:
                return None, None, None

            # Step 2: Filter repetitive content
            if REPEATIATION_CHECK_REQUIRED and self._is_repetitive_transcript(
                transcript
            ):
                return None, None, None

            # Step 3-5: Process transcript through text pipeline
            response, audio_response = await self.process_text(
                transcript=transcript,
                project=project,
                conversation_history=conversation_history,
                language=language,
            )

            generate_benchmark_report()

            return transcript, response, audio_response

        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None, None, None

    async def process_text(
        self,
        transcript: str,
        project: SessionProject,
        conversation_history: Optional[List[Conversation]] = None,
        language: str = "en",
        tts_provider: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[bytes]]:
        \"\"\"Process text through the pipeline: RAG -> LLM -> TTS\"\"\"
        try:
            if not transcript or not transcript.strip():
                return None, None

            # Step 1: RAG (Knowledge Base) if knowledge_base_ids are present
            rag_context = ""

            if project:
                timings["Started - RAG Query"] = time.perf_counter()
                rag_response = await KnowledgeBaseService.get_rag_context(
                    project.id, transcript
                )
                timings["Ended - RAG Query"] = time.perf_counter()
                rag_context = rag_response

            logger.info(f"RAG context: {rag_context}")

            # Step 2: Prepare messages for LLM (include RAG context if available)
            messages = self._prepare_chat_messages(
                transcript, rag_context, conversation_history
            )

            logger.info(f"Prepared messages for LLM: {messages}")

            # Step 3: Get AI response
            timings["Started - LLM Response"] = time.perf_counter()
            response = await self.llm_service.generate_response(
                messages, max_tokens=200
            )
            timings["Ended - LLM Response"] = time.perf_counter()

            if not response:
                return "", None

            # Step 4: Convert response to speech
            timings["Started - TTS Generation"] = time.perf_counter()
            audio_response = await self.tts_service.generate_audio(
                response, language, tts_provider
            )
            timings["Ended - TTS Generation"] = time.perf_counter()

            return response, audio_response

        except Exception as e:
            logger.error(f"Error processing text: {str(e)}")
            return None, None

    def _prepare_chat_messages(
        self,
        transcript: str,
        context: Optional[str],
        conversation_history: Optional[List[Conversation]],
    ) -> List[Dict]:
        \"\"\"Prepare messages for chat completion\"\"\"
        messages = []

        logger.info(f"Preparing chat messages for transcript: {transcript}")
        logger.info(f"Conversation history: {conversation_history}")
        logger.info(f"Context: {context}")

        # Add RAG context (when implemented)
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})

        # Add recent conversation history (last 4 exchanges)
        if conversation_history:
            # Convert Conversation objects to dicts
            messages.extend(
                [
                    c.model_dump() if hasattr(c, "model_dump") else dict(c)
                    for c in conversation_history[-4:]
                ]
            )

        # Add current user message
        messages.append({"role": "user", "content": transcript})

        logger.debug(f"Chat messages: {messages}")

        return messages
"""
    with open("app/services/voice_processor.py", "w") as f:
        f.write(services_code)

    # utils/constants.py
    utils_code = """from app.models.service_models.whisper_model import WhisperModelConfig

API_VERSION = "api/v1"


# Whisper model configuration for transcription

DEFAULT_WHISPER_CONFIG = WhisperModelConfig()

HIGH_ACCURACY_WHISPER_CONFIG = WhisperModelConfig(
    model_size="large-v3",  # Use a larger model for higher accuracy
    language="en",
    device="auto",
    compute_type=None,  # Auto-detect
    beam_size=5,  # More beams for better decoding
    best_of=5,
    temperature=0.0,
    condition_on_previous_text=False,
    initial_prompt=None,
    suppress_blank=True,
    suppress_tokens=[-1],
    without_timestamps=True,
    max_initial_timestamp=0.0,
    word_timestamps=False,
    vad_filter=True,
    vad_parameters={
        "threshold": 0.6,
        "min_speech_duration_ms": 500,
        "max_speech_duration_s": 30,  # Allow longer speech for accuracy
        "min_silence_duration_ms": 200,
        "speech_pad_ms": 50,
    },
)

REPEATIATION_CHECK_REQUIRED = True  # Enable repetitive transcript check
"""
    with open("app/utils/constants.py", "w") as f:
        f.write(utils_code)

    # middleware/api_middleware.py
    middleware_code = """from fastapi import FastAPI, Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional, List
import time
import logging
import uuid
import json

from app.services.api_services.auth_service import AuthService


SECRET_KEY = "CEnE7JPV9yB4SSPQqd974No0X7rmupOUrcTjVqjbvP9yFvhqsWhv0Lhn9WRgT4Vv"
ALGORITHM = "HS256"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APICallMiddleware(BaseHTTPMiddleware):
    \"\"\"
    Middleware for handling API calls in FastAPI
    - Logs request and response details
    - Adds request ID to track requests across the system
    - Measures request processing time
    - Handles errors gracefully
    - Validates Bearer token or Basic Auth
    \"\"\"

    def __init__(
        self,
        app: FastAPI,
        exclude_paths: Optional[List[str]] = None,
        secret_key: str = "CEnE7JPV9yB4SSPQqd974No0X7rmupOUrcTjVqjbvP9yFvhqsWhv0Lhn9WRgT4Vv",
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.secret_key = secret_key  # Secret key for token validation

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip middleware for excluded paths
        print("APICallMiddleware.py -> dispatch()")
        print("request path", request.url.path)
        if request.url.path.startswith("/api/v1/voice/ws/voice") or request.url.path.startswith("/api/v1/voice/call"):
            return await call_next(request)

        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        try:
            # Extract Authorization header
            auth_header = request.headers.get("authorization")
            if not auth_header:
                print("Authorization header not found")
                raise HTTPException(
                    status_code=401, detail="Missing Authorization header"
                )

            scheme, _, credentials = auth_header.partition(" ")
            if scheme.lower() == "bearer":
                user_payload = AuthService.validate_jwt_token(credentials)
                if not user_payload:
                    raise HTTPException(
                        status_code=401, detail="Invalid or expired token"
                    )
                request.state.user = user_payload
            else:
                raise HTTPException(
                    status_code=401, detail="Unsupported authentication scheme"
                )

            # Process the request
            response = await call_next(request)
            process_time = time.time() - start_time

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except HTTPException as http_exc:
            return Response(
                content=json.dumps(
                    {"error": http_exc.detail, "request_id": request_id}
                ),
                status_code=http_exc.status_code,
                media_type="application/json",
                headers={"X-Request-ID": request_id},
            )

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error {request_id}: {e} after {process_time:.3f}s")
            return Response(
                content=json.dumps(
                    {
                        "error": "Internal Server Error",
                        "request_id": request_id,
                        "detail": str(e),
                    }
                ),
                status_code=500,
                media_type="application/json",
                headers={"X-Request-ID": request_id},
            )
"""
    with open("middleware/api_middleware.py", "w") as f:
        f.write(middleware_code)

    # main.py
    main_code = """import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.models.shared_base import Base
from app.core.environment import env
from fastapi.middleware.cors import CORSMiddleware
from app.utils.response_builder import common_response
from app.routes.user import router as user_router
from app.routes.knowledgebase import router as knowledgebase_router
from app.routes.chat import router as chat_router
from app.routes.llm import router as llm_router
from middleware.APICallMiddleware import APICallMiddleware
from app.routes.voice import router as voice_router
from app.routes.hook import router as hook_router
from app.routes.agent import router as agent_router
from app.routes.dashboard import router as dashboard_router
from app.services.benchmark_service import set_label, get_benchmark_summary

from app.models.db_models import user_model, organization_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await env.db_client.create_tables(Base)
    logger.info("Connected to PostgresQL")
    yield
    await env.db_client.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Convo AI",
        description="Convo AI Lab",
        version="0.0.1",
        lifespan=lifespan,
    )

    # CORS setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(
    #     APICallMiddleware,
    #     exclude_paths=[
    #         "/docs",
    #         "/openapi.json",
    #         "/redoc",
    #         "/static",
    #         "/favicon.ico",
    #         "/api/v1/hook",
    #     ],
    # )

    app.include_router(user_router)
    app.include_router(knowledgebase_router)
    app.include_router(chat_router)
    app.include_router(llm_router)
    app.include_router(voice_router)
    app.include_router(hook_router)
    app.include_router(agent_router)
    app.include_router(dashboard_router)

    @app.get("/health")
    def check_health():
        return common_response("Application is running")

    if env.environment == "dev":

        @app.post("/benchmark")
        def benchmark(label: str):
            set_label(label)
            return common_response(f"Benchmark label set {label}")

        @app.get("/benchmark")
        def get_benchmarks():
            benchmark_summary = get_benchmark_summary()
            return common_response("Benchmark summary", data=benchmark_summary)

    return app


app = create_app()
"""
    with open("main.py", "w") as f:
        f.write(main_code)

    # requirements.txt
    requirements_code = """fastapi[standard]==0.115.12
pydantic==2.11.3
python-dotenv==1.1.0
SQLAlchemy[asyncio]==2.0.41
asyncpg==0.27.0
gtts==2.5.4
edge_tts==7.0.2
openai==1.84.0
faster-whisper==1.1.1
python-jose==3.4.0
whisper>=1.1.10
soundfile>=0.13.1
kokoro==0.9.2
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements_code)

    # Create virtual environment and install dependencies
    print("Creating virtual environment...")
    subprocess.check_call(["uv", "venv", ".venv"])

    print("Installing dependencies...")
    subprocess.check_call(["uv", "pip", "install", "-r", "requirements.txt"])

    print("Project setup complete! Activate the venv with 'source .venv/bin/activate' (Unix) or '.venv\\Scripts\\activate' (Windows). Run the app with 'uvicorn main:app --reload'.")