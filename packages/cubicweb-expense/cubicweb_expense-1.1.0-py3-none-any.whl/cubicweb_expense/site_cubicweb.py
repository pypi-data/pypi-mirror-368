# -*- coding: utf-8 -*-
try:
    from cubicweb import server

    server.ON_COMMIT_ADD_RELATIONS.add("has_lines")
except ImportError:
    pass

options = (
    (
        "logo-filename",
        {
            "type": "string",
            "default": "/some/path/to/logo.png",
            "help": "path to the logo used to build pdfs",
            "group": "expense",
            "level": 2,
        },
    ),
    (
        "company-name",
        {
            "type": "string",
            "default": "MyCompany",
            "help": "name of the company editing PDFs",
            "group": "expense",
            "level": 2,
        },
    ),
    (
        "company-address",
        {
            "type": "string",
            "default": "1, Rue du chat qui pêche - 75005 Paris",
            "help": "address of the company editing PDFs",
            "group": "expense",
            "level": 2,
        },
    ),
    (
        "company-offnum",
        {
            "type": "string",
            "default": "123.456.789.00011",
            "help": "official ID number of the company editing PDFs",
            "group": "expense",
            "level": 2,
        },
    ),
    (
        "company-actnum",
        {
            "type": "string",
            "default": "101AZ",
            "help": "activity number of the company editing PDFs",
            "group": "expense",
            "level": 2,
        },
    ),
)
