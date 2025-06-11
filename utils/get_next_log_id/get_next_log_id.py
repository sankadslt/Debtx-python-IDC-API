async def get_next_sequence(db, sequence_name: str) -> int:
        result = await db["collection_sequence"].find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True
        )
        return result["seq"]
    