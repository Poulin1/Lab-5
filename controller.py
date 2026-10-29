"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""


class Controller:

    def __init__(self, view, restaurant):
        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number):
        self.view.set_controller(TableController(self.view, self.restaurant,
                                                 self.restaurant.tables[table_number]))
        self.view.update()


class TableController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self, printer):
        self.view.set_controller(BillingController(self.view, self.restaurant, self.table,printer))
        self.view.update()
    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):

    def __init__(self, view, restaurant, table, seat_number):
        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        self.order.add_item(menu_item)
        self.restaurant.notify_views()
        self.view.update()

    def remove(self, order_item):
        self.order.remove_item(order_item)
        self.restaurant.notify_views()
        self.view.update()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()
        self.view.update()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()
        self.view.update()

class BillingController(Controller):
    def __init__(self, view, restaurant,table,printer):
        super().__init__(view, restaurant)
        self.table = table
        self.printer = printer

    def create_ui(self):
        self.view.create_billing_ui(self.table)

    def make_combine(self):
        self.view.set_controller(CombiningController(self.view, self.restaurant, self.table))
        self.view.update()

    def seat_bill(self, seat_number):
        order = self.table.order_for(seat_number)
        unbilled_items = [item for item in order.items if item.status != 'billed']

        if unbilled_items:
            table_idx = self.restaurant.tables.index(self.table)
            self.printer.print(f'--- Table {table_idx}, Seat {seat_number} ---')

            seat_total = 0
            for item in unbilled_items:
                self.printer.print(f'{item.details.name:<20} ${item.details.price:>5.2f}')
                seat_total += item.details.price

            self.printer.print('-' * 28)
            self.printer.print(f'{"Total:":<20} ${seat_total:>5.2f}')
            self.printer.print('============================\n')
            self.view.update()

    def finished_billing(self):
        self.printer.clear()
        self.table.clear_orders()
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()

    def print_billing(self):
        table_total = 0

        self.printer.print(f'== Combined Bill: Table {self.restaurant.tables.index(self.table)} ==')

        for seat_number in range(self.table.n_seats):
            order = self.table.order_for(seat_number)
            unbilled_items = [item for item in order.items if item.status != 'billed']
            if unbilled_items:
                self.printer.print(f'-- Seat {seat_number} --')
                for item in unbilled_items:
                    self.printer.print(f'{item.details.name:<20} ${item.details.price:>5.2f}')
                    table_total += item.details.price
                    item.mark_as_billed()

        if not self.table.has_unbilled_items():
            self.printer.print('-' * 28)
            self.printer.print(f'{"Table Total:":<20} ${table_total:>5.2f}')
            self.printer.print('============================\n')
        else:
            self.printer.print('No unbilled items remaining.')
            self.printer.print('============================\n')

        self.view.update()

    def cancel_bills(self):
        table_idx = self.restaurant.tables.index(self.table)
        self.printer.print(f'--- Table {table_idx} ---')
        self.printer.print("Cancelling Bills")
        self.printer.print("Item status reverted to 'ordered'")
        # Revert the data states in the model
        self.table.revert_billing()
        self.view.update()
        self.return_to_table()

    def return_to_table(self):
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.view.update()


class CombiningController(Controller):
    def __init__(self, view, restaurant,table):
        super().__init__(view, restaurant)
        self.table = table
        self.combined_seats = []

    def create_ui(self):
        self.view.create_combining_ui(self.table)

    def combine_orders(self):
        paying_seat = self.combined_seats.pop(0)
        paying_seat_order = self.table.order_for(paying_seat)

        for seat in self.combined_seats:
            order = self.table.order_for(seat)
            for item in list(order.items):
                paying_seat_order.add_item(item)
                order.remove_item(item)

        self.combined_seats.clear()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.view.update()


    def cancel_combining(self):
        pass

    def combine_seat_touch(self,seat_number):
        self.combined_seats.append(seat_number)