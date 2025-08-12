import asyncio
import os
import shutil
from pathlib import Path
import aiofiles
import aiofiles.os
import py7zr

class FileService:
    # async def zip_folder(self, folder_path: str, output_path: str):
    #     buffer = BytesIO()
        
    #     with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    #         for root, _, files in os.walk(folder_path):
    #             for file in files:
    #                 full_path = os.path.join(root, file)
    #                 arcname = os.path.relpath(full_path, folder_path)

    #                 async with aiofiles.open(full_path, "rb") as f:
    #                     content = await f.read()
    #                     zip_file.writestr(arcname, content)
        
    #     async with aiofiles.open(output_path, "wb") as f:
    #         await f.write(buffer.getvalue())
            
    # async def extract_zip(self, folder_path_zip: str, output_path: str):
    #         if not await aiofiles.os.path.exists(folder_path_zip):
    #             raise FileNotFoundError(
    #                 f"Arquivo ZIP não encontrado: {folder_path_zip}"
    #             )

    #         if not await aiofiles.os.path.exists(output_path):
    #             await aiofiles.os.makedirs(output_path, exist_ok=True)

    #         loop = asyncio.get_event_loop()
    #         await loop.run_in_executor(
    #             None, self._extrair_zip, folder_path_zip, output_path
    #         )

    # async def remove_file(self, file_path: str):
    #     if await aiofiles.os.path.exists(file_path):
    #         await aiofiles.os.remove(file_path)
            
    # async def remove_folder(self, folder_path: str):
    #     if await aiofiles.os.path.exists(folder_path):
    #         loop = asyncio.get_running_loop()
    #         await loop.run_in_executor(None, shutil.rmtree, folder_path)
            
    # def _extrair_zip(self, folder_path_zip: str, output_path: str):
    #     with zipfile.ZipFile(folder_path_zip, "r") as zip_ref:
    #         zip_ref.extractall(output_path)
            
    ################################################################################
    
    def __init__(self, threads: int = 1):
        # Se não especificado, usa todos os núcleos disponíveis
        self.threads = threads or os.cpu_count()

    async def compress_folder(self, folder_path: str, output_path: str):
        """
        Compacta uma pasta inteira para .7z de forma mais robusta.
        """
        if not await aiofiles.os.path.exists(folder_path):
            raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        await asyncio.to_thread(
            self._compress_folder_sync, folder_path, output_path
        )

    def _compress_folder_sync(self, folder_path: str, output_path: str):
        # Tentar diferentes configurações em ordem de preferência
        configurations = [
            # Configuração 1: LZMA2 com preset
            {"filters": [{"id": py7zr.FILTER_LZMA2, "preset": py7zr.PRESET_DEFAULT}]},
            
            # Configuração 2: LZMA2 com parâmetros manuais válidos
            {"filters": [{"id": py7zr.FILTER_LZMA2, "dict_size": 16777216}]},  # 16MB
            
            # Configuração 3: Padrão sem filtros customizados
            {}
        ]

        last_error = None
        for i, config in enumerate(configurations):
            try:
                print(f"Tentando configuração {i + 1}...")
                with py7zr.SevenZipFile(output_path, mode="w", **config) as archive:
                    archive.writeall(folder_path, arcname="")
                print(f"Sucesso com configuração {i + 1}!")
                return
            except Exception as e:
                print(f"Configuração {i + 1} falhou: {e}")
                last_error = e
                continue
        
        # Se todas as configurações falharam
        raise Exception(f"Todas as configurações falharam. Último erro: {last_error}")

    async def extract_file(self, file_path_7z: str, output_path: str):
        """
        Extrai um arquivo .7z de forma assíncrona.
        """
        if not await aiofiles.os.path.exists(file_path_7z):
            raise FileNotFoundError(f"Arquivo 7z não encontrado: {file_path_7z}")

        os.makedirs(output_path, exist_ok=True)

        await asyncio.to_thread(
            self._extract_7z_sync, file_path_7z, output_path
        )

    def _extract_7z_sync(self, file_path_7z: str, output_path: str):
        with py7zr.SevenZipFile(file_path_7z, mode="r") as archive:
            archive.extractall(path=output_path)

    async def remove_file(self, file_path: str):
        """
        Remove um arquivo de forma assíncrona.
        """
        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)

    async def remove_folder(self, folder_path: str):
        """
        Remove uma pasta inteira de forma assíncrona.
        """
        if await aiofiles.os.path.exists(folder_path):
            await asyncio.to_thread(shutil.rmtree, folder_path)