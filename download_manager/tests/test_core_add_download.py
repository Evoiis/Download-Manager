import asyncio
import pytest
import os
import logging

from dmanager.core import DownloadManager, DownloadState

def test_add_download():
    dm = DownloadManager()
    mock_url = "https://example.com/file.bin"
    mock_file_name = "test_file.bin"

    task_id = dm.add_download(mock_url, mock_file_name)
    
    download_metadata = dm.get_downloads()[task_id]

    assert download_metadata.url == mock_url
    assert download_metadata.output_file == mock_file_name

@pytest.mark.asyncio
async def test_output_file_with_invalid_characters():
    dm = DownloadManager()
    mock_url = "https://example.com/file.bin"
    mock_file_names = {
        "report:Q1.txt":        "reportQ1.txt",
        "budget/2026.xlsx":     "budget2026.xlsx",
        "notes*final?.md":      "notesfinal.md",
        'quote"test".txt':      "quotetest.txt",
        "data<raw>.csv":        "dataraw.csv",
        "pipe|name.log":        "pipename.log",
        "trailingspace.txt ":   "trailingspace.txt",
        "trailingdot.":         "trailingdot",
        "mix<>:\"/\\|?*.txt":   "mix.txt",
        "   .":                 "",
        "hello?.mp4":           "hello.mp4"
    }

    for invalid_name, fixed_name in mock_file_names.items():
        task_id = dm.add_download(mock_url, invalid_name)
        download_metadata = dm.get_downloads()[task_id]
        logging.debug(f"{download_metadata.output_file}, {fixed_name}, {download_metadata.output_file == fixed_name}")
        assert download_metadata.url == mock_url
        assert download_metadata.output_file == fixed_name, f"Failed to change invalid file name to fixed file name. Received: {invalid_name}, Expected: {fixed_name}"
    

@pytest.mark.asyncio
async def test_invalid_test_id(async_thread_runner):
    pass

@pytest.mark.asyncio
async def test_empty_output_file_name(monkeypatch, async_thread_runner):
    pass

@pytest.mark.asyncio
async def test_input_invalid_url(monkeypatch, async_thread_runner):
    pass

@pytest.mark.asyncio
async def test_input_already_used_output_file(monkeypatch, async_thread_runner):
    pass
