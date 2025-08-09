Secrets
=======

.. automodule:: terminusgps.aws.secrets
    :members:

=====
Usage
=====

Use :py:func:`~terminusgps.aws.secrets.get_secret` to retrieve an AWS `secretsmanager <https://docs.aws.amazon.com/secretsmanager/>`_ secret.

:py:func:`~terminusgps.aws.secrets.get_secret` returns a dictionary containing the secret values.

.. code:: python

    from terminusgps.aws.secrets import get_secret

    secret = get_secret("terminusgps-site-env-dev")
    print(secret["WIALON_TOKEN"]) # "my-secure-wialon-token"
