# Tax Calculator API app

This Flask-based REST API calculates one's owed taxes based on tax bracket information retrieved from [The Points Interview Test Server](https://github.com/Points/interview-test-server/)

## Request

GET requests to the app should be structured as follows:

```
	/api/v1/calculate-tax/<tax_year>/?income=<income_value>
```

where the parameters are defined as

- income_value - the value of one's annual income represented in __cents__.
- tax_year - the year for which the tax information should be retrieved.



## Return

The API will return a JSON response structured as follows:

```
{
	"effective_rate": 0.15,
    "income": 5000000,
    "tax_brackets": [
        {
            "max": 5019700,
            "min": 0,
            "owed": 750000.0,
            "rate": 0.15
        },
        {
            "max": null,
            "min": 5019700,
            "owed": 0,
            "rate": 0.205
        },
    ],
    "total_owed": 750000.0
}
```