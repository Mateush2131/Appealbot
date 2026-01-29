from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from config import config
from keyboards.inline import get_yes_no_keyboard
from services.api_client import APIClient

router = Router()
api_client = APIClient()

# Проверяем включены ли платежи
if not config.bot.enable_payments:
    # Если платежи отключены, не регистрируем обработчики
    pass
else:
    @router.message(Command("premium"))
    async def cmd_premium(message: Message):
        """Премиум подписка"""
        await message.answer(
            "🌟 <b>Премиум подписка</b>\n\n"
            "Преимущества:\n"
            "✅ Приоритетная поддержка\n"
            "✅ Возможность прикреплять файлы\n"
            "✅ Расширенная статистика\n"
            "✅ Быстрый ответ от администраторов\n\n"
            "Стоимость: 299₽/месяц\n\n"
            "Хотите оформить подписку?",
            parse_mode="HTML",
            reply_markup=get_yes_no_keyboard("premium_subscription", 1)
        )
    
    @router.callback_query(F.data.startswith("confirm:premium_subscription:"))
    async def process_premium_confirmation(callback: CallbackQuery):
        """Подтверждение покупки премиума"""
        action = callback.data.split(":")[3]
        
        if action == "yes":
            # Отправляем счет
            prices = [LabeledPrice(label="Премиум подписка (1 месяц)", amount=29900)]
            
            await callback.bot.send_invoice(
                chat_id=callback.from_user.id,
                title="Премиум подписка",
                description="Подписка на премиум функции на 1 месяц",
                payload="premium_subscription_monthly",
                provider_token=config.payment_token,  # Токен от платежной системы
                currency="RUB",
                prices=prices,
                start_parameter="premium_subscription",
                need_email=True,
                need_phone_number=False
            )
        
        await callback.answer()
    
    @router.pre_checkout_query()
    async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
        """Обработка предварительного чекаута"""
        await pre_checkout_query.bot.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query.id,
            ok=True
        )
    
    @router.message(F.successful_payment)
    async def process_successful_payment(message: Message):
        """Обработка успешного платежа"""
        user_id = message.from_user.id
        
        # Обновляем статус пользователя в базе
        # Здесь можно добавить логику активации премиума
        
        await message.answer(
            "🎉 <b>Оплата прошла успешно!</b>\n\n"
            "Ваш премиум доступ активирован на 30 дней.\n"
            "Теперь вам доступны все премиум функции!",
            parse_mode="HTML"
        )
    
    @router.message(Command("balance"))
    async def cmd_balance(message: Message):
        """Проверка баланса"""
        # Здесь можно реализовать проверку баланса
        await message.answer(
            "💰 <b>Ваш баланс</b>\n\n"
            "Текущий баланс: 0₽\n"
            "Премиум активен: Нет\n"
            "Доступно платежей: 0\n\n"
            "Используйте /premium для покупки подписки.",
            parse_mode="HTML"
        )

# ⚠️ ВАЖНО: Добавьте эту функцию в КОНЕЦ файла
def register_payment_handlers(dp):
    """Регистрация обработчиков платежей"""
    if config.bot.enable_payments:
        dp.include_router(router)
    # Если платежи отключены, функция ничего не делает