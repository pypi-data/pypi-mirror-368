Notifications
=============

.. autoclass:: terminusgps.aws.notifications.AsyncNotificationManager
    :members:
    :exclude-members: __weakref__
    :member-order: groupwise
    :autoclasstoc:

=====
Usage
=====

With an :py:obj:`~terminusgps.aws.notifications.AsyncNotificationManager`, you can asyncronously dispatch sms messages or voice calls.

Within an asyncronous event loop, i.e. :py:func:`main`, open an asyncronous context manager with ``async with``.

Within the context manager, :py:obj:`await` the :py:meth:`~terminusgps.aws.notifications.AsyncNotificationManager.send_sms` or :py:meth:`~terminusgps.aws.notifications.AsyncNotificationManager.send_voice` methods to dispatch your message.

.. code:: python

    import asyncio
    from terminusgps.aws.notifications import AsyncNotificationManager

    async def main() -> None:
        async with AsyncNotificationManager() as manager:
            # This is the message we will dispatch in this example
            message: str = "We know where ours are... do you?"

            # Send the message via sms to a single phone number
            await manager.send_sms("+15555555555", message)

            # Send the message via voice to a single phone number
            await manager.send_voice("+15555555555", message)

            # Send the message via sms to multiple phone numbers
            await manager.batch_send_sms(["+17135555555", "+15555555555"], message)

            # Send the message via sms to a single phone number with feedback
            await manager.send_sms("+15555555555", message, feedback=True)

            # Send the message via sms to a single phone number as a dry run
            await manager.send_sms("+15555555555", message, dry_run=True)
        return

    if __name__ == "__main__":
        asyncio.run(main())
