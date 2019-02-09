_perms_self_read_only = [
    {
        "principal": "SELF",
        "action":    "READ_ONLY"
    }
]

_perms_self_read_write = [
    {
        "principal": "SELF",
        "action":    "READ_WRITE"
    }
]

_perms_self_hide = [
    {
        "principal": "SELF",
        "action":    "HIDE"
    }
]

# a dump of an okta user schema with some example
# properties (int, bool)
okta_user_schema = {
    "id":          "https://paracelsus.okta.com/meta/schemas/user/default",
    "$schema":     "http://json-schema.org/draft-04/schema#",
    "name":        "user",
    "title":       "User",
    "description": "Okta user profile template with default permission settings",
    "lastUpdated": "2019-02-04T14:38:16.000Z",
    "created":     "2018-07-23T08:46:45.000Z",
    "definitions": {
        "custom": {
            "id":         "#custom",
            "type":       "object",
            "properties": {
                "abool": {
                    "title":       "A bool",
                    "description": "A boolean variable",
                    "type":        "boolean",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "anint": {
                    "title":       "An int",
                    "description": "An integer value",
                    "type":        "integer",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
            },
        },
        "base":   {
            "id":         "#base",
            "type":       "object",
            "properties": {
                "login":             {
                    "title":       "Username",
                    "type":        "string",
                    "required":    True,
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "minLength":   5,
                    "maxLength":   100,
                    "pattern":     ".+",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "firstName":         {
                    "title":       "First name",
                    "type":        "string",
                    "required":    True,
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "minLength":   1,
                    "maxLength":   50,
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "lastName":          {
                    "title":       "Last name",
                    "type":        "string",
                    "required":    True,
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "minLength":   1,
                    "maxLength":   50,
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "middleName":        {
                    "title":       "Middle name",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "honorificPrefix":   {
                    "title":       "Honorific prefix",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "honorificSuffix":   {
                    "title":       "Honorific suffix",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "email":             {
                    "title":       "Primary email",
                    "type":        "string",
                    "required":    True,
                    "format":      "email",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "title":             {
                    "title":       "Title",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "displayName":       {
                    "title":       "Display name",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "nickName":          {
                    "title":       "Nickname",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "profileUrl":        {
                    "title":       "Profile Url",
                    "type":        "string",
                    "format":      "uri",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "secondEmail":       {
                    "title":       "Secondary email",
                    "type":        "string",
                    "format":      "email",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "mobilePhone":       {
                    "title":       "Mobile phone",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "maxLength":   100,
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "primaryPhone":      {
                    "title":       "Primary phone",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "maxLength":   100,
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "streetAddress":     {
                    "title":       "Street address",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "city":              {
                    "title":       "City",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "state":             {
                    "title":       "State",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "zipCode":           {
                    "title":       "Zip code",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "countryCode":       {
                    "title":       "Country code",
                    "type":        "string",
                    "format":      "country-code",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "postalAddress":     {
                    "title":       "Postal Address",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_hide,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "preferredLanguage": {
                    "title":       "Preferred language",
                    "type":        "string",
                    "format":      "language-code",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "locale":            {
                    "title":       "Locale",
                    "type":        "string",
                    "format":      "locale",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "timezone":          {
                    "title":       "Time zone",
                    "type":        "string",
                    "format":      "timezone",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "userType":          {
                    "title":       "User type",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "employeeNumber":    {
                    "title":       "Employee number",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "costCenter":        {
                    "title":       "Cost center",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "organization":      {
                    "title":       "Organization",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "division":          {
                    "title":       "Division",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "department":        {
                    "title":       "Department",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_write,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "managerId":         {
                    "title":       "ManagerId",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                },
                "manager":           {
                    "title":       "Manager",
                    "type":        "string",
                    "mutability":  "READ_WRITE",
                    "scope":       "NONE",
                    "permissions": _perms_self_read_only,
                    "master":      {"type": "PROFILE_MASTER"}
                }
            },
            "required":   [
                "login",
                "firstName",
                "lastName",
                "email"
            ]
        }
    },
    "type":        "object",
    "properties":  {
        "profile": {
            "allOf": [
                {
                    "$ref": "#/definitions/custom"
                },
                {
                    "$ref": "#/definitions/base"
                }
            ]
        }
    }
}
