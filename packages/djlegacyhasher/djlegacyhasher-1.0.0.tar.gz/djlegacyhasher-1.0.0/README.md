# djlegacyhasher

Django application that provides reading django's old abandoned password hashers:

- SHA1PasswordHasher
- MD5PasswordHasher
- UnsaltedSHA1PasswordHasher
- UnsaltedMD5PasswordHasher

These classes can be used for read passwords from databases of legacy django projects that use corresponding hashing algorithms.

## Quick setup

Put the app into INSTALLED_APPS in settings.py::

    INSTALLED_APPS = [
        ...
        "legacyhasher",
    ]

To provide reading of one of old password hashing algorithms you need to add it's corresponding class into PASSWORD_HASHERS in settings.py, e.g.::

    PASSWORD_HASHERS = [
        ...
        "legacyhasher.hashers.SHA1PasswordHasher",
    ]

This will allow you to read SHA1 salted passwords from database. Once user logs in with his password, password will be saved to database using default hashing algorithm.
