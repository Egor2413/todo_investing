from sqlalchemy import ( create_engine, Integer, String, DateTime, Boolean,
                         BigInteger, SmallInteger, ForeignKey, Float)
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from config import DATABASE_URL
from datetime import datetime

engine = create_engine(
    DATABASE_URL,
    echo=True
)

session = sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


class ToDoList(Base):
    __tablename__ = "todo_list"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task: Mapped[str] = mapped_column(String(150), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    done_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class MonthlyStats(Base):
    __tablename__ = "monthly_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    points: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    target_points: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class FinancialAccount(Base):
    __tablename__ = "financial_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    transactions = relationship("FinancialTransaction", back_populates="account", cascade="all, delete-orphan")


class FinancialGoals(Base):
    __tablename__ = "financial_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    current_amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_achieved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now,
                                                          onupdate=datetime.now)


class FinancialTransaction(Base):
    __tablename__ = "financial_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_account.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)  # income, expense, transfer
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # сумма в рублях
    description: Mapped[str] = mapped_column(String(255), nullable=True)  # "Пополнение", "Покупка BTC" и т.д.
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    account = relationship("FinancialAccount", back_populates="transactions")



class Security(Base):
    __tablename__ = "security"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    security_type: Mapped[str] = mapped_column(String(25), nullable=False)
    location: Mapped[str] = mapped_column(String(25), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    value: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    risk_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=5)
    avg_dividents: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("financial_account.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now,
                                                          onupdate=datetime.now)
    snapshots = relationship("SecuritySnapshot", back_populates="security", cascade="all, delete-orphan")



class SecuritySnapshot(Base):
    __tablename__ = "security_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    security_id: Mapped[int] = mapped_column(Integer, ForeignKey("security.id"), nullable=False)

    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    month: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    price: Mapped[int] = mapped_column(Integer, nullable=False)  # цена на начало месяца
    total_value: Mapped[int] = mapped_column(Integer, nullable=False)  # общая стоимость (price * quantity)
    profit_loss: Mapped[float] = mapped_column(Float, nullable=False)  # прибыль/убыток за месяц
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    security = relationship("Security", back_populates="snapshots")


# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С БД =====

def add_task(task_title: str, due_date: str, value: int) -> int:
    """Добавить новую задачу. Возвращает ID задачи."""
    with session() as db:
        new_task = ToDoList(
            task=task_title,
            due_date=datetime.strptime(due_date, "%Y-%m-%d"),
            value=value,
            is_done=False,
        )
        db.add(new_task)
        db.commit()
        return new_task.id

def get_active_tasks() -> list:
    """Получить все активные (невыполненные) задачи."""
    with session() as db:
        return db.query(ToDoList).filter(ToDoList.is_done == False).all()

def get_completed_tasks() -> list:
    """Получить все выполненные задачи."""
    with session() as db:
        return db.query(ToDoList).filter(ToDoList.is_done == True).all()

def get_completed_tasks_by_month(year: int, month: int) -> list:
    """Получить выполненные задачи за указанный месяц."""
    with session() as db:
        return db.query(ToDoList).filter(
            ToDoList.is_done == True,
            db.func.strftime('%Y-%m', ToDoList.done_date) == f"{year}-{month:02d}"
        ).all()

def complete_task(task_id: int) -> int:
    """Отметить задачу выполненной. Возвращает количество баллов."""
    with session() as db:
        task = db.query(ToDoList).filter(ToDoList.id == task_id).first()
        if task:
            task.is_done = True
            task.done_date = datetime.now()
            db.commit()
            return task.value
        return 0

def delete_task(task_id: int) -> bool:
    """Удалить задачу. Возвращает True если успешно."""
    with session() as db:
        task = db.query(ToDoList).filter(ToDoList.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return True
        return False

def get_task_by_id(task_id: int):
    """Получить задачу по ID."""
    with session() as db:
        return db.query(ToDoList).filter(ToDoList.id == task_id).first()


def update_monthly_stats(points: int):
    """Добавить баллы за текущий месяц"""
    now = datetime.now()
    year = now.year
    month = now.month

    with session() as db:
        # Ищем запись за текущий месяц
        stats = db.query(MonthlyStats).filter(
            MonthlyStats.year == year,
            MonthlyStats.month == month
        ).first()

        if stats:
            stats.points += points
        else:
            stats = MonthlyStats(
                year=year,
                month=month,
                points=points,
                target_points=0  # или задай цель по умолчанию
            )
            db.add(stats)

        db.commit()

def get_monthly_stats(year: int, month: int):
    """Получить статистику за указанный месяц"""
    with session() as db:
        return db.query(MonthlyStats).filter(
            MonthlyStats.year == year,
            MonthlyStats.month == month
        ).first()

def get_last_n_months_stats(n: int = 12) -> list:
    """Получить статистику за последние N месяцев"""
    with session() as db:
        return db.query(MonthlyStats).order_by(
            MonthlyStats.year.desc(),
            MonthlyStats.month.desc()
        ).limit(n).all()


def get_average_monthly_points() -> float:
    """Получить средний балл в месяц за всё время"""
    with session() as db:
        stats = db.query(MonthlyStats).all()
        if not stats:
            return 0.0
        total_points = sum(s.points for s in stats)
        return total_points / len(stats)


# ============================================
# ФУНКЦИИ ДЛЯ ФИНАНСОВ (БАЗОВЫЕ)
# ============================================

def get_balance_by_currency() -> dict:
    """Получить баланс по каждой валюте"""
    with session() as db:
        results = db.query(
            FinancialAccount.currency,
            func.sum(FinancialAccount.balance).label('total')
        ).group_by(FinancialAccount.currency).all()
        
        return {currency: total for currency, total in results}

def get_accounts_by_type(account_type: str = None) -> list:
    """Получить список счетов (опционально по типу)"""
    with session() as db:
        query = db.query(FinancialAccount)
        if account_type:
            query = query.filter(FinancialAccount.account_type == account_type)
        return query.all()

def get_balance_by_type(account_type: str) -> int:
    """Получить сумму балансов по типу счёта"""
    with session() as db:
        total = db.query(func.sum(FinancialAccount.balance)).filter(
            FinancialAccount.account_type == account_type).scalar()
        return total or 0

def get_account_by_id(account_id: int) -> int:
    """Получить счёт по ID"""
    with session() as db:
        return db.query(FinancialAccount).filter(FinancialAccount.id == account_id).first()

def add_account(account_type: str, name: str, currency: str, balance: int) -> int:
    """Добавить новый счёт. Возвращает ID созданного счёта."""
    with session() as db:
        new_account = FinancialAccount(account_type=account_type, name=name, currency=currency, balance=balance)
        db.add(new_account)
        db.commit()
        return new_account.id

def update_balance(account_id: int, amount: int) -> int:
    """
    Изменить баланс счёта (прибавить amount).
    Для снятия передавайте отрицательное число.
    Возвращает новый баланс.
    Если баланс становится отрицательным — не меняем и возвращаем -1.
    """
    with session() as db:
        account = db.query(FinancialAccount).filter(FinancialAccount.id == account_id).first()
        if account:
            new_balance = account.balance + amount
            if new_balance < 0:
                return -1  # ❌ баланс не может быть отрицательным
            account.balance = new_balance
            db.commit()
            return account.balance
        return -1


# ============================================
# ФУНКЦИИ ДЛЯ ЦЕЛЕЙ
# ============================================

def get_goals() -> list:
    """Получить список всех целей"""
    with session() as db:
        return db.query(FinancialGoals).filter(FinancialGoals.is_achieved == False).all()


def get_goal_by_id(goal_id: int):
    """Получить цель по ID"""
    with session() as db:
        return db.query(FinancialGoals).filter(FinancialGoals.id == goal_id).first()


def add_goal(name: str, target_amount: int, deadline: str = None) -> int:
    """Добавить новую цель. Возвращает ID цели."""
    with session() as db:
        new_goal = FinancialGoals(
            name=name,
            target_amount=target_amount,
            current_amount=0,
            is_achieved=False
        )
        if deadline:
            new_goal.deadline = datetime.strptime(deadline, "%Y-%m-%d")
        db.add(new_goal)
        db.commit()
        return new_goal.id


def add_money_to_goal(goal_id: int, amount: int) -> int:
    """Пополнить цель вручную. Возвращает новый current_amount."""
    with session() as db:
        goal = db.query(FinancialGoals).filter(FinancialGoals.id == goal_id).first()
        if goal:
            goal.current_amount += amount
            if goal.current_amount > goal.target_amount:
                goal.current_amount = goal.target_amount
            db.commit()
            return goal.current_amount
        return 0


def complete_goal_manually(goal_id: int) -> bool:
    """Завершить цель вручную (is_achieved = True)."""
    with session() as db:
        goal = db.query(FinancialGoals).filter(FinancialGoals.id == goal_id).first()
        if goal:
            goal.is_achieved = True
            db.commit()
            return True
        return False


def delete_goal(goal_id: int) -> bool:
    """Удалить цель (отменить)."""
    with session() as db:
        goal = db.query(FinancialGoals).filter(FinancialGoals.id == goal_id).first()
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False


def get_active_goals() -> list:
    """Получить только активные (невыполненные) цели."""
    with session() as db:
        return db.query(FinancialGoals).filter(
            FinancialGoals.is_achieved == False
        ).all()


def get_achieved_goals() -> list:
    """Получить выполненные цели."""
    with session() as db:
        return db.query(FinancialGoals).filter(
            FinancialGoals.is_achieved == True
        ).all()

def get_transactions_by_account(account_id: int, limit: int = 50) -> list:
    """Получить транзакции по счёту (последние limit штук)"""
    with session() as db:
        return db.query(FinancialTransaction).filter(
            FinancialTransaction.account_id == account_id
        ).order_by(FinancialTransaction.transaction_date.desc()).limit(limit).all()


def update_balance(account_id: int, amount: int, description: str = "") -> int:
    with session() as db:
        account = db.query(FinancialAccount).filter(FinancialAccount.id == account_id).first()
        if account:
            new_balance = account.balance + amount
            if new_balance < 0:
                return -1

            # Создаём транзакцию
            transaction_type = "income" if amount > 0 else "expense"
            transaction = FinancialTransaction(
                account_id=account_id,
                transaction_type=transaction_type,
                amount=abs(amount),
                description=description or ("Пополнение" if amount > 0 else "Снятие")
            )
            db.add(transaction)

            account.balance = new_balance
            db.commit()
            return account.balance
        return -1


# ============================================
# ФУНКЦИИ ДЛЯ ИНВЕСТИЦИЙ
# ============================================

def add_asset(name: str, asset_type: str, quantity: float, price: float, risk_level: int, account_id: int = 1) -> int:
    """Добавить новый актив. Возвращает ID актива."""
    with session() as db:
        new_asset = Security(
            name=name,
            security_type=asset_type,
            location="portfolio",  # по умолчанию
            quantity=quantity,
            value=price,  # текущая цена = цена покупки
            risk_level=risk_level,
            avg_dividents=0,
            account_id=account_id
        )
        db.add(new_asset)
        db.commit()
        return new_asset.id


def get_portfolio() -> list:
    """Получить все активы в портфеле"""
    with session() as db:
        return db.query(Security).all()


def get_asset_by_id(asset_id: int):
    """Получить актив по ID"""
    with session() as db:
        return db.query(Security).filter(Security.id == asset_id).first()


def update_asset_price(asset_id: int, new_price: float) -> float:
    """Обновить текущую цену актива. Возвращает новую цену."""
    with session() as db:
        asset = db.query(Security).filter(Security.id == asset_id).first()
        if asset:
            asset.value = new_price
            db.commit()
            return asset.value
        return 0


def sell_asset(asset_id: int, quantity: float) -> tuple:
    """
    Продать часть актива.
    Возвращает (новое_количество, выручка)
    Если продаётся всё -> удаляет актив и возвращает (0, выручка)
    """
    with session() as db:
        asset = db.query(Security).filter(Security.id == asset_id).first()
        if not asset:
            return (0, 0)

        if quantity >= asset.quantity:
            # Продаём всё
            revenue = asset.quantity * asset.value
            db.delete(asset)
            db.commit()
            return (0, revenue)
        else:
            # Продаём часть
            revenue = quantity * asset.value
            asset.quantity -= quantity
            db.commit()
            return (asset.quantity, revenue)


def get_portfolio_value() -> float:
    """Общая стоимость портфеля (сумма quantity * value)"""
    with session() as db:
        assets = db.query(Security).all()
        total = sum(a.quantity * a.value for a in assets)
        return total


def get_portfolio_profit() -> tuple:
    """
    Рассчитать доходность портфеля.
    Возвращает (общая_прибыль_в_рублях, процент_доходности)
    """
    with session() as db:
        assets = db.query(Security).all()
        total_cost = 0
        total_value = 0

        for a in assets:
            cost = a.quantity * a.value  # текущая стоимость
            total_value += cost
            # Для расчёта прибыли нужна цена покупки
            # Упрощённо: считаем что value = текущая цена
            # В реальности нужно хранить покупки отдельно

        # Пока заглушка
        return (0, 0.0)


def get_portfolio_risk() -> dict:
    """
    Рассчитать риски портфеля.
    Возвращает средний риск и распределение по типам
    """
    with session() as db:
        assets = db.query(Security).all()
        if not assets:
            return {"avg_risk": 0, "by_type": {}}

        total_risk = sum(a.risk_level for a in assets)
        avg_risk = total_risk / len(assets)

        risk_by_type = {}
        for a in assets:
            t = a.security_type
            if t not in risk_by_type:
                risk_by_type[t] = []
            risk_by_type[t].append(a.risk_level)

        # Усредняем по типам
        for t in risk_by_type:
            risk_by_type[t] = sum(risk_by_type[t]) / len(risk_by_type[t])

        return {"avg_risk": avg_risk, "by_type": risk_by_type}


def create_monthly_snapshot(year: int, month: int) -> int:
    """Создать ежемесячный снимок портфеля. Возвращает количество записей."""
    with session() as db:
        assets = db.query(Security).all()
        count = 0

        for asset in assets:
            snapshot = SecuritySnapshot(
                security_id=asset.id,
                year=year,
                month=month,
                price=asset.value,
                total_value=asset.quantity * asset.value,
                profit_loss=0  # нужно рассчитывать относительно прошлого месяца
            )
            db.add(snapshot)
            count += 1

        db.commit()
        return count


# ============================================
# ФУНКЦИИ ДЛЯ ИНВЕСТИЦИЙ (ДОПОЛНИТЕЛЬНЫЕ)
# ============================================

def get_current_quarter() -> tuple:
    """Возвращает (год, квартал) для текущей даты"""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return now.year, quarter


def get_quarter_start(year: int, quarter: int) -> datetime:
    """Возвращает первый день квартала (1 января, 1 апреля, 1 июля, 1 октября)"""
    month = (quarter - 1) * 3 + 1
    return datetime(year, month, 1)


def get_next_quarter_start() -> datetime:
    """Возвращает дату начала следующего квартала"""
    year, quarter = get_current_quarter()
    if quarter == 4:
        year += 1
        quarter = 1
    else:
        quarter += 1
    return get_quarter_start(year, quarter)


def is_snapshot_window_open() -> bool:
    """Проверяет, открыто ли окно для создания снимка (1-10 число первого месяца квартала)"""
    now = datetime.now()
    year, quarter = get_current_quarter()
    first_month = (quarter - 1) * 3 + 1
    return now.month == first_month and 1 <= now.day <= 10


def get_snapshot_history() -> list:
    """Получить все снимки с информацией о кварталах"""
    with session() as db:
        return db.query(SecuritySnapshot).order_by(
            SecuritySnapshot.year.desc(),
            SecuritySnapshot.month.desc()
        ).all()


def get_snapshot_by_date(year: int, month: int) -> list:
    """Получить снимок за конкретный месяц/год"""
    with session() as db:
        return db.query(SecuritySnapshot).filter(
            SecuritySnapshot.year == year,
            SecuritySnapshot.month == month
        ).all()


def check_asset_exists(name: str) -> bool:
    """Проверить, существует ли актив с таким названием"""
    with session() as db:
        return db.query(Security).filter(Security.name == name).first() is not None


def get_asset_by_name(name: str):
    """Получить актив по названию"""
    with session() as db:
        return db.query(Security).filter(Security.name == name).first()


def add_to_existing_asset(asset_id: int, quantity: float, price: float) -> float:
    """
    Добавить количество и цену к существующему активу с усреднением.
    Возвращает новую среднюю цену.
    """
    with session() as db:
        asset = db.query(Security).filter(Security.id == asset_id).first()
        if not asset:
            return 0

        # Усреднение цены
        total_quantity = asset.quantity + quantity
        total_cost = asset.quantity * asset.value + quantity * price
        new_avg_price = total_cost / total_quantity if total_quantity > 0 else 0

        asset.quantity = total_quantity
        asset.value = new_avg_price

        db.commit()
        return new_avg_price
