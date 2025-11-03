import tkinter as tk
from tkinter import messagebox


class WorkoutTracker:
    """Handles the business logic for tracking workouts, independent of the UI."""

    def __init__(self):
        self.workouts = []

    def add_workout(self, workout, duration_str):
        """Validates and adds a workout. Returns a tuple (bool, str) for success and a message."""
        if not workout or not duration_str:
            return False, "Please enter both workout and duration."

        try:
            duration = int(duration_str)
            if duration <= 0:
                return False, "Duration must be a positive number."

            self.workouts.append({"workout": workout, "duration": duration})
            return True, f"'{workout}' added successfully!"
        except ValueError:
            return False, "Duration must be a number."

    def get_workout_list_text(self):
        """Formats the list of workouts for display."""
        if not self.workouts:
            return "No workouts logged yet."

        workout_list = "Logged Workouts:\n"
        for i, entry in enumerate(self.workouts):
            workout_list += f"{i+1}. {entry['workout']} - {entry['duration']} minutes\n"
        return workout_list


class FitnessTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("ACEestFitness and Gym")

        # Labels and Entries for adding workouts
        self.workout_label = tk.Label(master, text="Workout:")
        self.workout_label.grid(row=0, column=0, padx=5, pady=5)
        self.workout_entry = tk.Entry(master)
        self.workout_entry.grid(row=0, column=1, padx=5, pady=5)

        self.duration_label = tk.Label(master, text="Duration (minutes):")
        self.duration_label.grid(row=1, column=0, padx=5, pady=5)
        self.duration_entry = tk.Entry(master)
        self.duration_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        self.add_button = tk.Button(
            master, text="Add Workout", command=self.add_workout
        )
        self.add_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.view_button = tk.Button(
            master, text="View Workouts", command=self.view_workouts
        )
        self.view_button.grid(row=3, column=0, columnspan=2, pady=5)

        # The UI class now uses a logic handler
        self.tracker = WorkoutTracker()

    def add_workout(self):
        workout = self.workout_entry.get()
        duration_str = self.duration_entry.get()

        # Delegate the logic to the tracker
        success, message = self.tracker.add_workout(workout, duration_str)

        if success:
            messagebox.showinfo("Success", message)
            self.workout_entry.delete(0, tk.END)
            self.duration_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)

    def view_workouts(self):
        workout_list = self.tracker.get_workout_list_text()
        messagebox.showinfo("Workouts", workout_list)


if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()

# End of ACEest_Fitness.py