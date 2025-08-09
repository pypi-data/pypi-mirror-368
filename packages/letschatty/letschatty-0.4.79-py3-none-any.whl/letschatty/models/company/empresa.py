from pydantic import Field, ConfigDict, field_validator, SecretStr, model_validator
from typing import Optional, List, Dict
from ..base_models import ChattyAssetModel
from letschatty.models.channels.channel import WhatsAppClientInfo

class EmpresaModel(ChattyAssetModel):
    name: str = Field(description="The name of the company")
    frozen_name: str = Field(description="The frozen name of the company", frozen=True)
    industry: Optional[str] = Field(default = "")
    url: Optional[str] = Field(default = "")
    allowed_origins: list[str] = Field(default_factory=lambda: [])
    company_email: Optional[str] = Field(default = "")
    contributor_count: Optional[str] = Field(default = "")
    purpose_of_use_chatty: Optional[List[str]] = Field(default_factory=lambda: [])
    current_wpp_approach: Optional[str] = Field(default = "")
    main_reason_to_use_chatty: Optional[str] = Field(default = "")
    active: Optional[bool] = Field(default = True)
    friendly_aliases: list[str] = Field(description="The friendly aliases of the company used for the enviamewhats.app links", default_factory=lambda: [])
    terms_of_service_agreement: Optional[bool] = Field(default = False)
    self_display_phone_number: Optional[str] = Field(description="The display phone number user's write to", default = None, alias="display_phone_number")
    self_phone_number_id: Optional[str] = Field(description="The phone number id of the company", alias="phone_number_id", default = None)
    self_bussiness_account_id: Optional[str] = Field(description="The WABA - WhatsApp Business Account id of the company", default = None, alias="bussiness_account_id")
    photo_url: str = Field(default = "")
    self_meta_token: Optional[str] = Field(default = None, alias="meta_token")
    slack_channels: Dict[str,Dict[str,str]] = Field(default_factory=lambda:{})
    phone_numbers_for_testing: list[str] = Field(default_factory=lambda: [])
    analytics : Optional[bool] = Field(default = True)
    dataset_id: Optional[str] = Field(default = None, description="To notify events to Meta Conversions API")
    hammer_credentials: Optional[Dict[str,str]] = Field(default = None, description="Only usef for hammer propiedades real state agencies")
    continuous_conversation_template_name: Optional[str] = Field(default = None, description="The name of the continuous conversation template")

    model_config = ConfigDict(
        populate_by_name=True
    )


    @model_validator(mode="before")
    def validate_frozen_name(cls, data: Dict) -> Dict:
        if "frozen_name" not in data:
            data["frozen_name"] = data["name"].replace(" ", "_")
        return data

    @field_validator("name", mode="before")
    def validate_name(cls, v):
        return v

    @property
    def active_continuous_conversation_template_name(self) -> str:
        if not self.continuous_conversation_template_name:
            raise ValueError(f"continuous_conversation_template_name is not set for company {self.name}")
        return self.continuous_conversation_template_name

    @property
    def waba_id(self) -> str:
        return self.bussiness_account_id

    @property
    def database_name(self):
        return "chatty-db"

    @property
    def whatsapp_channel(self) -> WhatsAppClientInfo:
        if self.active_for_messaging:
            return WhatsAppClientInfo(
                display_phone_number=self.display_phone_number,
                business_phone_number_id=self.phone_number_id,
                waba_id=self.bussiness_account_id,
                access_token=SecretStr(self.meta_token),
                dataset_id=self.dataset_id
            )
        else:
            raise ValueError(f"Company {self.name} is not active for messaging")

    @property
    def friendly_alias(self):
        return self.friendly_aliases[0]

    @property
    def display_phone_number(self):
        if self.self_display_phone_number is None:
            raise ValueError(f"display_phone_number is not set for company {self.name}")
        return self.self_display_phone_number

    @property
    def phone_number_id(self):
        if self.self_phone_number_id is None:
            raise ValueError(f"phone_number_id is not set for company {self.name}")
        return self.self_phone_number_id

    @property
    def bussiness_account_id(self):
        if self.self_bussiness_account_id is None:
            raise ValueError(f"bussiness_account_id is not set for company {self.name}")
        return self.self_bussiness_account_id

    @property
    def meta_token(self):
        if self.self_meta_token is None:
            raise ValueError(f"meta_token is not set for company {self.name}")
        return self.self_meta_token

    @property
    def active_for_messaging(self) -> bool:
        try:
            self.meta_token
            self.phone_number_id
            self.bussiness_account_id
            self.display_phone_number
            return True
        except ValueError:
            return False
