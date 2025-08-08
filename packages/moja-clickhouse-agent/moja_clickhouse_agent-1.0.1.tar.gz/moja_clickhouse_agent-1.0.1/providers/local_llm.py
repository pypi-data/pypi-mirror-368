"""
Local LLM provider using an OpenAI-compatible server (llama.cpp / llamafile / llama-cpp-python)
"""

from typing import Dict, List, Any, Optional
import httpx
import os
import platform
import stat
import subprocess
import time
from pathlib import Path
from datetime import datetime
from utils.logging import get_logger
try:
    from rich.console import Console
    from rich.progress import Progress, BarColumn, TimeRemainingColumn, DownloadColumn, TextColumn
    _console: Optional[Console] = Console()
except Exception:
    _console = None

logger = get_logger(__name__)


class LocalLLMProvider:
    """OpenAI-compatible local LLM HTTP client"""

    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", model: str = "qwen3-1.7b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0, headers={"Content-Type": "application/json"})

        # Optional request logging
        self.logs_dir = "logs/local_llm_requests"
        os.makedirs(self.logs_dir, exist_ok=True)

        # Ensure local server is running; if not, download and start it for single-user use
        try:
            if not self._is_server_ready():
                self._announce("Setting up local LLM (Qwen3 1.7B) …")
                self._bootstrap_and_start_server()
                # Wait until ready
                self._wait_until_ready(timeout_seconds=180)
                self._announce("Local LLM is ready on http://127.0.0.1:1234")
        except Exception as e:
            logger.error(f"Failed to ensure local LLM server: {e}")
            raise

    def _log(self, request: Dict[str, Any], response: Optional[Dict[str, Any]] = None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = os.path.join(self.logs_dir, f"local_llm_{timestamp}.json")
        import json
        with open(path, "w") as f:
            json.dump({"request": request, "response": response}, f, indent=2, ensure_ascii=False)

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
        live_animation=None,
    ) -> Dict[str, Any]:
        """Call /v1/chat/completions on a local OpenAI-compatible server.

        Note: Many llama.cpp servers do not support tool calling yet. We pass tools when available,
        but callers should handle the case where no tool calls are returned.
        """

        body: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            body["tools"] = tools
            body["tool_choice"] = "auto"

        url = f"{self.base_url}/chat/completions"
        self._log(body)

        resp = await self.client.post(url, json=body)
        if resp.status_code != 200:
            logger.error(f"Local LLM error {resp.status_code}: {resp.text}")
            raise Exception(f"Local LLM error {resp.status_code}: {resp.text}")

        data = resp.json()
        self._log(body, data)
        return data

    async def close(self):
        await self.client.aclose()

    # --- bootstrap helpers ---
    def _is_server_ready(self) -> bool:
        try:
            url = f"{self.base_url}/models"
            # Some servers may not implement /models; try a lightweight POST to chat/completions
            r = httpx.get(url, timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        try:
            r = httpx.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "system", "content": "ping"}, {"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                    "temperature": 0.0,
                },
                timeout=2.0,
            )
            return r.status_code == 200
        except Exception:
            return False

    def _bootstrap_and_start_server(self):
        # Directories
        base_dir = Path.home() / ".local" / "share" / "moja"
        bin_dir = base_dir / "bin"
        models_dir = base_dir / "models"
        run_dir = base_dir / "run"
        for d in [bin_dir, models_dir, run_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Resolve platform and download llamafile binary (with fallback to llama-cpp-python)
        llama_path = bin_dir / "llamafile"
        have_llamafile = False
        if not llama_path.exists():
            try:
                self._announce("Downloading llama server (one time)…")
                self._download_llamafile(llama_path)
                llama_path.chmod(llama_path.stat().st_mode | stat.S_IEXEC)
                have_llamafile = True
            except Exception as e:
                logger.warning(f"llamafile download failed, will fallback to python server: {e}")
        else:
            have_llamafile = True

        # Download model if missing (default to Unsloth Q4_K_M)
        model_path = models_dir / "Qwen3-1.7B-Q4_K_M.gguf"
        if not model_path.exists():
            self._announce("Downloading Qwen3 1.7B (~1.3 GB) … this can take a few minutes")
            self._download_file(
                "https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf",
                model_path,
            )

        # Start server in background
        port = int(self.base_url.split(":")[-1].split("/")[0]) if ":" in self.base_url else 1234
        host = "127.0.0.1"
        self._announce("Starting local LLM server …")
        if have_llamafile and llama_path.exists():
            cmd = [
                str(llama_path),
                "--server",
                "--model",
                str(model_path),
                "--port",
                str(port),
                "--host",
                host,
                "--chat-template",
                "chatml",
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        else:
            # Fallback: use llama-cpp-python OpenAI-compatible server
            self._ensure_llama_cpp_server_installed()
            cmd = [
                self._python_exec(),
                "-m",
                "llama_cpp.server",
                "--model",
                str(model_path),
                "--host",
                host,
                "--port",
                str(port),
                "--chat_format",
                "chatml",
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    def _wait_until_ready(self, timeout_seconds: int = 60):
        start = time.time()
        while time.time() - start < timeout_seconds:
            if self._is_server_ready():
                return
            time.sleep(1)
        raise TimeoutError("Local LLM server did not become ready in time")

    def _download_llamafile(self, out_path: Path):
        system = platform.system().lower()
        machine = platform.machine().lower()
        if system != "darwin":
            raise RuntimeError("Auto-setup currently supports macOS only; falling back to python server")
        # Pick arch
        if "arm" in machine or "aarch64" in machine:  # Apple Silicon
            url = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.9.3/llamafile-macos-arm64"
        else:  # Intel
            url = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.9.3/llamafile-macos-x86_64"
        self._download_file(url, out_path)

    def _download_file(self, url: str, out_path: Path):
        with httpx.stream("GET", url, follow_redirects=True, timeout=None) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0
            task = None
            progress = None
            if _console is not None and total:
                progress = Progress(
                    TextColumn("{task.description}"),
                    BarColumn(),
                    DownloadColumn(),
                    TimeRemainingColumn(),
                    console=_console,
                )
                progress.start()
                task = progress.add_task(f"[cyan]Downloading…[/cyan]", total=total)
            try:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_bytes():
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress and task is not None:
                            progress.update(task, advance=len(chunk))
                        elif total and downloaded % (5 * 1024 * 1024) == 0:
                            self._announce(f"Downloaded {downloaded//(1024*1024)}MB / {total//(1024*1024)}MB")
            finally:
                if progress:
                    progress.stop()

    def _announce(self, message: str):
        logger.info(message)
        try:
            if _console is not None:
                _console.print(f"[cyan]{message}[/cyan]")
            else:
                print(message)
        except Exception:
            pass

    def _python_exec(self) -> str:
        return os.environ.get("PYTHON_EXECUTABLE") or (os.sys.executable or "python3")

    def _ensure_llama_cpp_server_installed(self):
        try:
            import importlib  # noqa: F401
            import llama_cpp.server  # type: ignore # noqa: F401
            return
        except Exception:
            self._announce("Installing llama-cpp-python server (one time)…")
            subprocess.check_call([self._python_exec(), "-m", "pip", "install", "--upgrade", "--prefer-binary", "llama-cpp-python[server]"])


