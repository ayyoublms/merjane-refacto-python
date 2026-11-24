# Current business behavior

This page records behavior in the current implementation. The tests preserve that behavior for regression coverage; they do not settle ambiguities in the exercise brief.

## NORMAL

- If stock is greater than zero, processing saves a one-unit decrement.
- If stock is zero, a delay notification is requested only when lead time is greater than zero.

## SEASONAL

- Stock is decremented only when today is strictly after the season start, strictly before the season end, and stock is positive. Both boundary dates are excluded by the current implementation.
- In other cases, the estimated restock date is compared with the season end. An arrival after the end requests an unavailability notification and sets stock to zero.
- If the season has not started and arrival is not after the season end, the service requests an unavailability notification and saves the product without changing stock.
- Remaining cases request a delay notification. Equality with the season end currently follows this path.

## EXPIRABLE

- If stock is positive and expiry is strictly in the future, processing saves a one-unit decrement.
- If expiry is today or earlier, the service sets stock to zero and requests an expiry notification.
- If stock is zero while expiry is in the future, the service still sets stock to zero and requests an expiry notification. The brief does not specify this stockout case.

## Unresolved questions

Confirm these cases with the exercise owner before changing the preserved behavior. Update the corresponding tests and this page after clarification.

| Case | Existing behavior covered by tests | What the brief leaves open |
|---|---|---|
| Today is the season start date | The product is treated as outside the season. | Whether the start date is included. |
| Today is the season end date | The product is treated as outside the season. | Whether the end date is included. |
| Restock arrives exactly on the season end date | A delay notification is sent because arrival does not exceed the end date. | Whether arrival on the end date is acceptable. |
| Today is the expiry date | The product is treated as expired, stock is set to zero, and an expiry notification is sent. | Whether the product remains sellable through the expiry date. |
| Stock is zero but expiry is in the future | Stock remains zero and an expiry notification is sent. | The brief gives no notification rule for an unexpired stockout. |
| Product type is unknown or its required date is missing | Unknown types are skipped. Missing dates may cause processing to fail. | The brief defines neither validation nor error responses for invalid product data. |
