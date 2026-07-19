from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any
from google.adk.agents.readonly_context import ReadonlyContext
from app.core.mongodb import get_mongodb_db

logger = logging.getLogger(__name__)

# Default prompts fallback mapping
DEFAULT_FALLBACKS = {
    "conversation_agent": "You are a clinical intake assistant. Extract symptoms from the patient conversation as structured JSON.",
    "doctor_agent": "You are a clinical documentation assistant. Generate a concise clinical summary. NEVER diagnose.",
    "followup_agent": "You are a clinical follow-up planning assistant for a rural primary health center in India. Generate follow-up plans, monitoring instructions, warning signs, lifestyle recommendations, and ASHA worker tasks.",
    "history_agent": "You are a medical records assistant. Summarize the patient's medical history concisely.",
    "medicine_agent": "You are a clinical pharmacology assistant. Check medications for interactions and safety.",
    "triage_agent": "You are a clinical triage assistant. Classify patient priority as LOW, MEDIUM, or HIGH.",
    "vision_agent": "You are a medical image description assistant. Describe visible findings objectively. NEVER diagnose.",
}

# Mapping of agent key to default prompt file name under app/prompts/
PROMPT_FILE_MAP = {
    "conversation_agent": "conversation.md",
    "doctor_agent": "doctor.md",
    "followup_agent": "followup.md",
    "history_agent": "history.md",
    "medicine_agent": "medicine.md",
    "triage_agent": "triage.md",
    "vision_agent": "vision.md",
}

class PromptManager:
    """Manages system prompts with support for DB overrides, environment variables, and file fallbacks."""

    def __init__(self, prompts_dir: Path | None = None):
        if prompts_dir is None:
            self.prompts_dir = Path(__file__).parent.parent / "prompts"
        else:
            self.prompts_dir = prompts_dir
        self._cache: dict[str, str] = {}

    def clear_cache(self) -> None:
        """Clear memory cache of prompts."""
        self._cache.clear()

    def get_prompt_sync(self, name: str) -> str:
        """Get the prompt synchronously from cache, environment, or file fallback."""
        # 1. Cache
        if name in self._cache:
            return self._cache[name]

        # 2. Env Override
        env_var_name = f"PROMPT_{name.upper()}"
        if env_var_name in os.environ:
            val = os.environ[env_var_name]
            self._cache[name] = val
            return val

        # 3. Local File
        filename = PROMPT_FILE_MAP.get(name)
        if filename:
            file_path = self.prompts_dir / filename
            try:
                content = file_path.read_text(encoding="utf-8")
                self._cache[name] = content
                return content
            except FileNotFoundError:
                logger.warning("Prompt file not found for %s at %s. Falling back to default.", name, file_path)
            except Exception as e:
                logger.error("Error reading prompt file for %s: %s", name, e)

        # 4. In-Memory fallback defaults
        fallback = DEFAULT_FALLBACKS.get(name, "You are a helpful clinical assistant.")
        self._cache[name] = fallback
        return fallback

    async def get_prompt(self, name: str) -> str:
        """Get the prompt asynchronously, prioritizing MongoDB, then environment, files, and hardcoded fallbacks."""
        # 1. Env Override (takes highest precedence for dev/test)
        env_var_name = f"PROMPT_{name.upper()}"
        if env_var_name in os.environ:
            return os.environ[env_var_name]

        # 2. Database Override
        try:
            db = get_mongodb_db()
            if db is not None:
                doc = await db["prompts"].find_one({"_id": name})
                if doc and "text" in doc:
                    return doc["text"]
        except Exception as e:
            logger.warning("Failed to load prompt %s from MongoDB: %s. Using file/cache fallback.", name, e)

        # 3. Cache or Local File Fallback
        return self.get_prompt_sync(name)

    async def set_prompt(self, name: str, text: str) -> None:
        """Update/Override a prompt in the database and clear local cache."""
        try:
            db = get_mongodb_db()
            if db is not None:
                await db["prompts"].replace_one(
                    {"_id": name},
                    {"_id": name, "text": text},
                    upsert=True
                )
                logger.info("Prompt %s successfully updated in MongoDB.", name)
            else:
                raise ConnectionError("MongoDB not initialized.")
        except Exception as e:
            logger.error("Failed to save prompt %s to MongoDB: %s", name, e)
            raise
        finally:
            if name in self._cache:
                del self._cache[name]

    async def reset_prompt(self, name: str) -> None:
        """Reset a prompt, removing it from MongoDB and local cache (reverts to file)."""
        try:
            db = get_mongodb_db()
            if db is not None:
                await db["prompts"].delete_one({"_id": name})
                logger.info("Prompt %s reset/deleted from MongoDB.", name)
        except Exception as e:
            logger.error("Failed to delete prompt %s from MongoDB: %s", name, e)
            raise
        finally:
            if name in self._cache:
                del self._cache[name]

    async def list_all_prompts(self) -> dict[str, dict[str, Any]]:
        """List all registered prompts with their origin (DB overridden or default file)."""
        results = {}
        db = None
        try:
            db = get_mongodb_db()
        except Exception:
            pass

        db_prompts = {}
        if db is not None:
            try:
                async for doc in db["prompts"].find({}):
                    db_prompts[doc["_id"]] = doc["text"]
            except Exception as e:
                logger.warning("Error fetching all prompts from MongoDB: %s", e)

        for name in PROMPT_FILE_MAP.keys():
            # Check if overridden in MongoDB
            is_overridden = name in db_prompts
            current_text = db_prompts[name] if is_overridden else self.get_prompt_sync(name)
            results[name] = {
                "name": name,
                "text": current_text,
                "is_overridden": is_overridden,
                "default_file": PROMPT_FILE_MAP[name],
            }
        return results

# Singleton instance of prompt manager
prompt_manager = PromptManager()

def make_instruction_provider(agent_name: str):
    """Creates a callable InstructionProvider for LlmAgent."""
    async def instruction_provider(ctx: ReadonlyContext) -> str:
        return await prompt_manager.get_prompt(agent_name)
    return instruction_provider
