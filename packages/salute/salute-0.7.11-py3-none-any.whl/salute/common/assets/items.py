def get_bubble(text: str) -> dict:
    return {"bubble": {"text": text}}


def get_card_list(content_url: str, content_hash: str) -> dict:
    return {
        "card": {
            "type": "list_card",
            "cells": [
                {
                    "type": "image_cell_view",
                    "content": {
                        "url": content_url,
                        "hash": content_hash,
                    },
                }
            ],
        }
    }


def get_suggestion(choices: list[str]) -> list[dict]:
    result = []
    for choice in choices:
        result.append(
            {
                "title": choice,
                "actions": [
                    {
                        "type": "text",
                        "text": choice,
                    }
                ],
            }
        )

    return result
