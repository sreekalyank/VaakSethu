"""
agent.py
--------
Triggers outbound calls via the Vapi API using your saved Assistant.
Supports single calls and bulk parallel dialing via CSV.
"""

import asyncio
import argparse
import httpx
import requests
import logging
import csv
from config import settings
from assistant import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"Bearer {settings.VAPI_API_KEY}",
    "Content-Type": "application/json",
}


def make_call(phone_number: str, prospect_name: str, context: str = "") -> dict:
    system_prompt = SYSTEM_PROMPT
    if context:
        system_prompt += f"\n\nProspect context: {context}"

    payload = {
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "assistantId": settings.VAPI_ASSISTANT_ID,

        "assistantOverrides": {
            "firstMessage": (
                f"Hi, is this {prospect_name}? "
                f"Great — I'm Alex calling from Tatvom Labs. "
                f"Do you have just 2 minutes?"
            ),
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "systemPrompt": system_prompt
            },
            "serverUrl": settings.WEBHOOK_URL,
        },

        "customer": {
            "number": phone_number,
            "name": prospect_name,
        },
    }

    logger.info(f"[CALLING] {prospect_name} at {phone_number}...")

    response = requests.post(
        "https://api.vapi.ai/call/phone",
        json=payload,
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code not in (200, 201):
        logger.error(f"❌ Error making call: {response.text}")
        response.raise_for_status()

    result = response.json()
    logger.info(f"✅ Call ID: {result.get('id')} - Status: {result.get('status')}")
    return result


async def make_call_async(client: httpx.AsyncClient, lead: dict, max_retries: int = 3) -> dict:
    system_prompt = SYSTEM_PROMPT
    context = lead.get("context", "")
    if context:
        system_prompt += f"\n\nProspect context: {context}"

    payload = {
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "assistantId": settings.VAPI_ASSISTANT_ID,

        "assistantOverrides": {
            "firstMessage": (
                f"Hi, is this {lead.get('name')}? "
                f"Great — I'm Alex calling from Tatvom Labs. "
                f"Do you have just 2 minutes?"
            ),
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "systemPrompt": system_prompt
            },
            "serverUrl": settings.WEBHOOK_URL,
        },

        "customer": {
            "number": lead.get("phone"),
            "name": lead.get("name"),
        },
    }

    for attempt in range(max_retries):
        try:
            response = await client.post(
                "https://api.vapi.ai/call/phone",
                json=payload,
                headers=HEADERS,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"✅ {lead.get('name')} ({lead.get('phone')}) → Call ID: {result.get('id')}")
            return {"lead": lead.get("name"), "phone": lead.get("phone"), "call_id": result.get("id")}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error for {lead.get('name')}: {e.response.text}")
            if attempt == max_retries - 1:
                return e
        except httpx.RequestError as e:
            logger.warning(f"Request failed for {lead.get('name')} (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return e
            
        await asyncio.sleep(2 ** attempt)  # Exponential backoff


async def dial_leads_parallel(leads: list[dict], concurrency: int = 10) -> list[dict]:
    logger.info(f"[BULK DIAL] Firing {len(leads)} calls (concurrency={concurrency})...")
    semaphore = asyncio.Semaphore(concurrency)

    async def dial_with_limit(client, lead):
        async with semaphore:
            return await make_call_async(client, lead)

    async with httpx.AsyncClient() as client:
        tasks = [dial_with_limit(client, lead) for lead in leads]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = [r for r in results if isinstance(r, dict)]
    failures = [r for r in results if isinstance(r, Exception)]

    logger.info(f"[SUMMARY] ✅ {len(successes)} calls initiated | ❌ {len(failures)} failed")
    return successes


def load_leads_from_csv(file_path: str) -> list[dict]:
    leads = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "phone" in row and "name" in row:
                    leads.append(row)
                else:
                    logger.warning(f"Skipping invalid row, missing 'phone' or 'name': {row}")
    except FileNotFoundError:
        logger.error(f"CSV file not found: {file_path}")
    return leads


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vapi Voice Sales Agent")
    parser.add_argument("--phone", help="Phone number in E.164 format")
    parser.add_argument("--name", help="Prospect name")
    parser.add_argument("--context", default="", help="Optional context")
    parser.add_argument("--bulk-csv", help="Path to CSV file for bulk dialing")

    args = parser.parse_args()

    if args.phone and args.name:
        make_call(args.phone, args.name, args.context)
    elif args.bulk_csv:
        leads = load_leads_from_csv(args.bulk_csv)
        if leads:
            asyncio.run(dial_leads_parallel(leads, concurrency=5))
        else:
            logger.warning("No valid leads found to dial.")
    else:
        print("Usage:")
        print("  Single call : python agent.py --phone +917013549646 --name 'Test'")
        print("  Bulk dial   : python agent.py --bulk-csv leads.csv")