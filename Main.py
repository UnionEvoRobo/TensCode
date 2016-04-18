from TensRobot import TensRobot, TensBuilder
from Point import Point
import sys

__author__ = 'James Boggs'

class Main(object):
    """
    The main code for Union's Tensegrity project. See the README for a complete
    overview. This code provides interactive user access to all the rest of the
    code, making using, testing, and evaluating tensegrities much nicer for all
    the people who didn't directly participate in this coding.
    """
    def __init__(self):
        # self.GA_machine = GeneticAlgorithm() TODO Make GeneticAlgorithm a thing
        self.tens_builder = TensBuilder()
        self.active_tens = None
        self.main_menu_loop()

    def main_menu_loop(self):
        """
        This is the main function of the Main object. It provides the user an
        interactive menu from which they can create new tensegrities, run the
        genetic algorithm on tensegrities, create a behavioral repertoire for a
        tensegrity, screw around with the tensegrity manually, and anything
        else added later. Eventually, this should be made into a GUI...
        """
        while True:
            if self.active_tens:
                home_msg = """
                Welcome to Tensegrity Control! The active tensegrity is {}.
                What would you like to do?
                1. Build a tensegrity
                2. Load a tensegrity
                3. Exit
                4. Test motors
                5. Move to location
                6. Run genetic algorithm
                7. Build behavioral repertoire
                8. Save tensegrity
                """.format(self.active_tens.name)
            else:
                home_msg = """
                Welcome to Tensegrity Control! What would you like to do?
                1. Build a tensegrity
                2. Load a tensegrity
                3. Exit
                """

            user_choice = input(">> ")

            if user_choice == 1: self.build_tens()
            elif user_choice == 2: self.load_tens()
            elif user_choice == 3: sys.exit()
            elif user_choice > 3 and not self.active_tens: print("Bad choice!")
            elif user_choice == 4: self.test_active()
            elif user_choice == 5: self.move_tens_to()
            elif user_choice == 6: self.run_GA()
            elif user_choice == 7: self.build_BR()
            elif user_choice == 8: self.save_tens()
            else: print("Bad choice!")

    def build_tens(self):
        if self.active_tens:
            save_tens = raw_input("Save the existing tensegrity first? (Y/N)")
            if save_tens.upper() == "Y":
                self.save_tens()
        self.active_tens = self.tens_builder.build_tens()

    def load_tens(self):
        print("Not implemented yet!")  # TODO Implement this #procrastination

    def test_active(self):
        print("Testing motors...")
        self.active_tens.test_motors()

    def move_tens_to(self):
        tgt_x = input("Target X position? ")
        tgt_y = input("Target Y position? ")
        tgt_theta = input("Target heading? ")
        target = Point(tgt_x, tgt_y, tgt_theta)
        print("Moving tensegrity to {}".format(target))
        self.active_tens.move_to_absolute(target)

    def run_GA(self):
        print("Not implemented yet!")  # TODO Implement this #procrastination

    def build_BR(self):
        print("Not implemented yet!")  # TODO Implement this #procrastination

    def save_tens(self):
        print("Not implemented yet!")  # TODO Implement this #procrastination


