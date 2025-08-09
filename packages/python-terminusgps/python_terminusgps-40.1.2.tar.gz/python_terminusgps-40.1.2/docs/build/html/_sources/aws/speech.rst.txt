Speech
======

.. autoclass:: terminusgps.aws.speech.AsyncSpeechSynthesisManager
    :members:
    :exclude-members: __weakref__
    :autoclasstoc:

=====
Usage
=====

.. code:: python

    import asyncio

    from terminusgps.aws.speech import AsyncSpeechSynthesisManager

    async def main() -> None:
        async with AsyncSpeechSynthesisManager("my-bucket-name") as manager:
            message: str = "This message should be read aloud and saved as a file in an S3 bucket."
            await manager.synthesize_speech(message)

    if __name__ == "__main__":
        asyncio.run(main())
