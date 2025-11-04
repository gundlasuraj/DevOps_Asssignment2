import tkinter as tk
from tkinter import messagebox
from workout_tracker import WorkoutTracker # Import from the new logic file

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
        workout_text = self._get_workout_list_text()
        messagebox.showinfo("Workouts", workout_text)

    def _get_workout_list_text(self):
        """Formats the list of workouts for display in the UI."""
        workouts = self.tracker.get_workouts()
        if not workouts:
            return "No workouts logged yet."

        workout_list_str = "Logged Workouts:\n"
        for i, entry in enumerate(workouts):
            workout_list_str += f"{i+1}. {entry['workout']} - {entry['duration']} minutes\n"
        return workout_list_str


if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()

# End of ACEest_Fitness.py