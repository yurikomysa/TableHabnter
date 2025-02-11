from datetime import date, timedelta

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import (
    Calendar,
    CalendarScope,
    CalendarUserConfig,
)
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Const, Format


RU_MONTHS = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

RU_WEEKDAYS = {
    0: "Понедельник", 1: "Вторник", 2: "Среда",
    3: "Четверг", 4: "Пятница", 5: "Суббота", 6: "Воскресенье"
}


class CustomCalendar(Calendar):
    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data, self.config,
                today_text=Const("***"),
                header_text=Format("> {month} {year} <").format(
                    month=lambda d, **kwargs: RU_MONTHS[d.month],
                    year=lambda d, **kwargs: d.year
                ),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data, self.config,
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data, self.config,
            ),
        }

    async def _get_user_config(
            self,
            data: dict,
            manager: DialogManager,
    ) -> CalendarUserConfig:
        return CalendarUserConfig(
            firstweekday=0,
            min_date=date.today(),
            max_date=(date.today() + timedelta(days=6 * 30))
        )

# Переводы

