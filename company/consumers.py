import json
import logging
from decimal import Decimal
from typing import List

from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import (
    ObserverModelInstanceMixin,
    action,
)

from .models import Company, Price, PriceUser
logger = logging.getLogger(__name__)


async def dump_decimal(value: Decimal):
    value = json.dumps(str(value))
    return value


class PriceConsumer(
    GenericAsyncAPIConsumer, AsyncAPIConsumer, ObserverModelInstanceMixin
):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code, *args, **kwargs):
        user: User = self.scope["user"]
        user_group = await self.get_user_group(user)
        for group in user_group:
            company_id = str(group['current_company_id'])
            group_company_name = f"Company_{company_id}"
            self.remove_user_to_company(company_id)
            await self.channel_layer.group_discard(
                group_company_name,
                self.channel_name
            )

    @action()
    async def join_company(self, pk, **kwargs):
        logger.info(f"User join company {self.scope['user'].id}")
        group_company_name = f"Company_{str(pk)}"
        await self.channel_layer.group_add(
            group_company_name, self.channel_name
        )
        await self.add_user_to_company(pk)

    @action()
    async def remove_company(self, pk, **kwargs):
        logger.info(f"User join company {self.scope['user'].id}")
        group_company_name = f"Company_{str(pk)}"
        await self.channel_layer.group_discard(
            group_company_name, self.channel_name
        )
        await self.remove_user_to_company(pk)

    async def send_group_message(self, company):


        active_group = await self.get_active_group(company)
        for group in active_group:
            company_id = group["current_company_id"]
            group_company_name = f"Company_{str(company_id)}"
            logger.info(f"Send group message {group_company_name}")
            data = {
                "id": str(company_id),
                "created_at": group.get(
                    "current_company__updated_at"
                ).strftime("%d/%m/%y %H:%M"),
                "value": str(group.get("current_company__last_price")),
            }
            await self.channel_layer.group_send(
                group_company_name, {"type": "send_new_price", **data}
            )

    @database_sync_to_async
    def get_active_group(self, new_price_objs):
        active_group = PriceUser.objects.filter(
            current_company__id__in=new_price_objs
        ).values(
            "current_company_id",
            "current_company__last_price",
            "current_company__updated_at",
        )
        return list(active_group)

    @database_sync_to_async
    def get_user_group(self, user):
        active_group = PriceUser.objects.filter(
            current_user=user
        ).values("current_company_id")
        return list(active_group)

    @action()
    async def update_prices(self, data, **kwargs):
        logger.info(f"Update price")
        company: List[Company] = await self.update_price_company(data)
        await self.send_group_message(company)
        await self.create_price(company)

    @database_sync_to_async
    def update_price_company(self, data):
        all_objs = Company.objects.filter(id__in=data.keys())
        for company in all_objs:
            company.last_price = data.get(str(company.id))
        Company.objects.bulk_update(all_objs, fields=["last_price"])
        return all_objs

    @database_sync_to_async
    def create_price(self, price_objs):
        Price.objects.bulk_create(
            [Price(company_id=q.id, value=q.last_price) for q in price_objs]
        )

    @database_sync_to_async
    def get_last_price(self, pk):
        last_price_obj = (
            Price.objects.filter(company_id=pk).order_by("created_at").last()
        )
        if last_price_obj is None:
            return 0
        return last_price_obj.value

    async def send_new_price(self, value):
        await self.send(text_data=json.dumps(value))

    @database_sync_to_async
    def get_company(self, pk: int) -> Company:
        return Company.objects.get(pk=pk)

    @database_sync_to_async
    def add_user_to_company(self, pk):
        user: User = self.scope["user"]
        if not PriceUser.objects.filter(
            current_user=user, current_company_id=pk
        ).exists():
            PriceUser.objects.create(current_user=user, current_company_id=pk)

    @database_sync_to_async
    def remove_user_to_company(self, pk):
        user: User = self.scope["user"]
        price_user = PriceUser.objects.get(
            current_user=user, current_company_id=pk
        )
        if price_user:
            price_user.delete()
