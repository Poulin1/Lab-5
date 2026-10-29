"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from constants import TABLES, MENU_ITEMS


class Restaurant:

    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:

    def __init__(self, seats, location):
        self.n_seats = seats
        self.location = location
        self.orders = [Order() for _ in range(seats)]

    def has_any_active_orders(self):
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False
    def has_unbilled_items(self):
        for order in self.orders:
            for item in order.items:
                if item.status != 'billed':
                    return True
        return False
    def has_billed_items(self):
        for order in self.orders:
            for item in order.items:
                if item.status == 'billed':
                    return True
        return False

    def revert_billing(self):
        for order in self.orders:
            for item in order.items:
                if item.status == 'billed':
                    item.status = 'ordered'
    def marked_as_printed(self):
        for order in self.orders:
            for item in order.items:
                if item.status == 'printed':
                    return True
        return False
    def clear_orders(self):
        self.orders=[Order() for _ in range(self.n_seats)]

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def order_for(self, seat):
        return self.orders[seat]



class Order:

    def __init__(self):
        self.items = []

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item):
        self.items.remove(order_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))


class OrderItem:
    def __init__(self, menu_item):
        self.details = menu_item
        self.status = 'requested'

    def mark_as_ordered(self):
        self.status = 'ordered'

    def mark_as_served(self):
        self.status = 'served'

    def mark_as_billed(self):
        self.status = 'billed'
    def mark_as_printed(self):
        self.status = 'printed'

    def has_been_ordered(self):
        return self.status in ['ordered', 'served', 'billed', 'printed']

    def has_been_served(self):
        return self.status in ['served', 'billed']

    def can_be_cancelled(self):
        return self.status == 'requested'



class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price
