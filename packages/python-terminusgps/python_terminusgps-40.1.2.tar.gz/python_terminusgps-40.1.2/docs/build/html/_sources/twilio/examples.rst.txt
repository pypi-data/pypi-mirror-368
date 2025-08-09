Usage Examples
==============

=====================================
Send an SMS message to a phone number
=====================================

.. code:: python

    import asyncio

    from terminusgps.twilio.caller import TwilioCaller


    async def main() -> None:
        phone: str = "+15555555555"
        msg: str = "Hello from Terminus GPS!"
        method: str = "sms" # Optional in this case, "sms" is default.
        with TwilioCaller() as caller:
            task = caller.create_notification(to_number=phone, message=msg)
            await task


    if __name__ == "__main__":
        asyncio.run(main())

===========================================
Send SMS messages to multiple phone numbers
===========================================

.. code:: python

    import asyncio

    from terminusgps.twilio.caller import TwilioCaller

    def main() -> None:
        phones: str = ["+17135555555", "+18325555555"]
        msg: str = "Hello from Terminus GPS!"
        method: str = "sms" # Optional in this case, "sms" is default.
        with TwilioCaller() as caller:
            tasks = [
                caller.create_notification(
                    to_number=num, message="Hello from Terminus GPS!", method=method
                )
                for num in phones
            ]
            asyncio.gather(*tasks)

    if __name__ == "__main__":
        main()

========================================
Call phone number and read message aloud
========================================

.. code:: python

    import asyncio

    from terminusgps.twilio.caller import TwilioCaller

    def main() -> None:
        phone: str = "+15555555555"
        msg: str = "Hello from Terminus GPS!"
        method: str = "call" # "phone" is an alias for "call", so "phone" would work too
        with TwilioCaller() as caller:
            task = caller.create_notification(
                to_number=phone, message="Hello from Terminus GPS!", method=method
            )
            await task

    if __name__ == "__main__":
        main()
