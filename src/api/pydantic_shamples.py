from pydantic import BaseModel, Field

class PaymentModel(BaseModel):
    tariff_id: int = Field(..., description="The ID of the tariff associated with the payment.")
    email: str = Field(..., description="The email address of the user making the payment.")
    method: str = Field(..., description="The payment method used for the transaction.")
    installment_months: int | None = Field(default=None, description="The number of months for the installment plan, if applicable.")
    promo_code: str | None = Field(default=None, description="The promotional code applied to the payment, if any.")
