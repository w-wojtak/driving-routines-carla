import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import Slider, Button


def plot_memory_decision_wm(u_field, u_dec, u_wm, field_pars, elapsed_time, message=None, fig=None, axes=None):
    """
    Plots u_field, u_dec, and u_wm in a single figure with three subplots in one row and three columns.
    """
    x_lim, dx, dt, _ = field_pars
    x = np.arange(-x_lim, x_lim + dx, dx)

    # If fig and axes are not provided, create a new figure
    if fig is None or axes is None:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    else:
        fig.clear()
        axes = fig.subplots(1, 3)

    # Plot u_field, u_dec, and u_wm in three subplots
    for i, (activity, label, y_lim) in enumerate(
            zip([u_field, u_dec, u_wm], ['u_field(x)', 'u_dec(x)', 'u_wm(x)'], [(-1, 10), (-10, 10), (-2, 3.5)])):
        axes[i].plot(x, activity)
        axes[i].set_xlim(-90, 30)
        axes[i].set_xticks([-60, -30, 0])
        axes[i].set_xticklabels(["Home", "Work", "School"])
        axes[i].set_ylim(y_lim)
        axes[i].set_title(label)
        axes[i].set_ylabel('Amplitude')

    # Calculate hours and minutes
    hours = int(elapsed_time // 60)
    minutes = int(elapsed_time % 60)

    fig.suptitle(f'Time: {hours:02d}:{minutes:02d}')

    # If message not empty, add a text field
    if message:
        for i in range(3):
            axes[i].annotate(message, xy=(0.5, 0),
                             xycoords=('axes fraction', 'figure fraction'),
                             xytext=(0, 5),
                             textcoords='offset points',
                             size=14, ha='center', va='bottom')

    # Draw the updated figure
    plt.draw()
    plt.pause(0.01)

    return fig, axes


def plot_activity_with_message(activity, field_pars, elapsed_time, message=None, fig=None):
    """
    Plots the activity at a given time step.
    """

    x_lim, dx, dt, _ = field_pars
    x = np.arange(-x_lim, x_lim + dx, dx)

    # If fig is not provided, create a new figure
    if fig is None:
        fig, ax = plt.subplots(figsize=(4, 3))
    else:
        ax = fig.gca()

    # Plot activity in the top part of the figure
    plt.plot(x, activity)
    plt.xlim(-90, 30)
    plt.ylim(-1, 10)
    plt.ylabel('u(x)')

    # Calculate hours and minutes
    hours = int(elapsed_time // 60)
    minutes = int(elapsed_time % 60)

    plt.title(f'time:  {hours:02d}:{minutes:02d}')

    plt.xticks([-60, -30, 0], ["Home", "Work", "School"])

    ax.set_aspect(8 / 1)

    # I message not empty, add a text field
    if message:
        ax.annotate(message,  # Your string

                    # The point that we'll place the text in relation to
                    xy=(0.5, 0),
                    # Interpret the x as axes coords, and the y as figure coords
                    xycoords=('axes fraction', 'figure fraction'),

                    # The distance from the point that the text will be at
                    xytext=(0, 5),
                    # Interpret `xytext` as an offset in points...
                    textcoords='offset points',

                    # Any other text parameters we'd like
                    size=14, ha='center', va='bottom')
        plt.pause(1)

    # Draw the updated figure
    plt.draw()

    # Add a short pause to allow the plot to update
    plt.pause(0.01)

    return fig, ax


def plot_activity_at_time_step(activity, field_pars, elapsed_time, fig=None):
    """
    Plots the activity at a given time step.
    """

    x_lim, dx, dt, _ = field_pars
    x = np.arange(-x_lim, x_lim + dx, dx)

    # If fig is not provided, create a new figure
    if fig is None:
        fig, ax = plt.subplots(figsize=(4, 3))
    else:
        ax = fig.gca()

    plt.plot(x, activity)
    plt.xlim(-90, 30)
    plt.ylabel('u(x)')

    # Update the title with formatted elapsed time
    plt.title(f'time:  {elapsed_time[:4]}')

    plt.xticks([-60, -30, 0], ["Home", "Work", "School"])

    # Draw the updated figure
    plt.draw()

    # Add a short pause to allow the plot to update
    plt.pause(0.01)

    return fig, ax


def plot_final_state_1d(activity, field_pars):
    """
    Plots the final state of u(x,t) at time t=end.
    """
    x_lim, _, dx, _, _ = field_pars
    x = np.arange(-x_lim, x_lim + dx, dx)

    plt.figure(figsize=(6, 5))
    plt.plot(x, activity[-1, :])
    plt.xlim(-x_lim, x_lim)
    plt.xlabel('x')
    plt.ylabel('u(x)')
    fig = plt.gcf()
    plt.show()

    return fig


def plot_animate_1d(activity, field_pars, inputs, input_flag):
    """
    Animates the time evolution of activity u(x,t) and inputs (if present).
    """
    x_lim, _, dx, _, _ = field_pars
    x = np.arange(-x_lim, x_lim + dx, dx)

    upper_lim_y = max([activity.max(), inputs.max()])
    lower_lim_y = min([activity.min(), inputs.min()])

    # enable interactive mode
    plt.ion()
    figure, ax = plt.subplots(figsize=(6, 4))
    ax.set_ylim(lower_lim_y, upper_lim_y)
    ax.set_xlim(-x_lim, x_lim)
    plt.xlabel('x')

    if input_flag:
        line1, = ax.plot(x, activity[0, :], label='u(x)')
        line2, = ax.plot(x, inputs[0, :], label='Input')

        ax.legend()

        for i in range(activity.shape[0]):
            if i % 5 == 0:
                line1.set_xdata(x)
                line1.set_ydata(activity[i, :])

                line2.set_xdata(x)
                line2.set_ydata(inputs[i, :])

                # draw updated values
                figure.canvas.draw()
                figure.canvas.flush_events()
                time.sleep(0.001)
    else:
        line1, = ax.plot(x, activity[0, :], label='u(x)')

        ax.legend()  # Add a legend to the plot

        for i in range(activity.shape[0]):
            if i % 5 == 0:
                line1.set_xdata(x)
                line1.set_ydata(activity[i, :])

                # draw updated values
                figure.canvas.draw()
                figure.canvas.flush_events()
                time.sleep(0.001)


def plot_slider_1d(activity, field_pars, inputs, input_flag):
    """
     Creates an interactive plot with a slider to visualize how activity and inputs change in time.
    """

    x_lim, _, dx, dt, _ = field_pars

    x = np.arange(-x_lim, x_lim + dx, dx)

    upper_lim_y = max([activity.max(), inputs.max()])
    lower_lim_y = min([activity.min(), inputs.min()])

    fig, ax = plt.subplots(figsize=(6, 4))
    plt.subplots_adjust(bottom=0.25)  # Adjust the bottom margin to make space for the slider and button

    line_activity, = ax.plot(x, activity[0, :], label='u(x)')

    if input_flag:
        line_input, = ax.plot(x, inputs[0, :], label='Input(x)', linestyle='dashed')

    ax.legend()
    ax.set_ylim(lower_lim_y, upper_lim_y)
    ax.set_xlim(-x_lim, x_lim)
    plt.xlabel('x')

    ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])  # Define the slider's position [left, bottom, width, height]
    slider = Slider(ax_slider, '', 0, activity.shape[0] - 1, valinit=0, valstep=1)
    slider.valtext.set_visible(False)  # hide matplotlib slider values

    ax_reset = plt.axes([0.8, 0.02, 0.1, 0.04])  # Define the reset button's position [left, bottom, width, height]
    reset_button = Button(ax_reset, 'Reset')

    time_label = plt.text(0.5, 0.05, f'Time Step: {slider.val * dt:.2f}', transform=fig.transFigure, ha='center')

    def update(val):
        time_step = int(slider.val)
        line_activity.set_ydata(activity[time_step, :])

        if input_flag:
            line_input.set_ydata(inputs[time_step, :])

        time_label.set_text(f'Time : {time_step * dt:.2f}')
        fig.canvas.draw_idle()

    def reset(event):
        slider.set_val(0)

    slider.on_changed(update)
    reset_button.on_clicked(reset)

    plt.show()


def plot_space_time_flat(activity, field_pars):
    """
    Plots a flat space-time image of the field activity.
    """
    x_lim, t_lim, _, _, _ = field_pars

    x_range = [-x_lim, x_lim]
    t_range = [0.0, t_lim]

    upper_lim = activity.max()
    lower_lim = activity.min()

    plt.figure(figsize=(6, 3))
    pic = plt.imshow(np.transpose(activity), cmap='plasma', vmin=lower_lim, vmax=upper_lim,
                     extent=[t_range[0], t_range[1], x_range[0], x_range[1]],
                     interpolation='nearest', origin='lower', aspect='auto')
    plt.colorbar(pic)
    plt.xlabel('t')
    plt.ylabel('x', rotation=0)
    plt.title('u(x,t)')
    plt.tight_layout()
    plt.gcf().set_dpi(300)
    fig = plt.gcf()
    plt.show()

    return fig


def plot_space_time_3d(activity, field_pars):
    """
    Plot a 3D surface of the field activity over space and time.
    """
    x_lim, t_lim, dx, dt, _ = field_pars

    upper_lim = activity.max()
    lower_lim = activity.min()

    x = np.arange(-x_lim, x_lim + dx, dx)
    t = np.arange(0, t_lim + dt, dt)

    x_mesh, t_mesh = np.meshgrid(x, t)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_surface(t_mesh, x_mesh, activity, cmap=plt.get_cmap('plasma'),
                           linewidth=0, antialiased=False)

    # Remove the gray shading
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    ax.set_box_aspect([2, 1, 1])

    fig.colorbar(surf, shrink=0.4, aspect=10, pad=0.2)

    ax.zaxis.set_rotate_label(False)

    ax.set_xlabel('t', linespacing=3.2)
    ax.set_ylabel('x', linespacing=3.1)
    ax.set_zlabel('u(x,t)', linespacing=3.4, rotation=0)

    ax.zaxis.labelpad = 10
    ax.set_zlim(lower_lim, upper_lim)

    ax.set_yticks(np.arange(-x_lim, x_lim + dx, 2))

    plt.show()


def plot_space_time_3d_contour(activity, field_pars):
    """
    Plot a 3D surface of the field activity over space and time with a contour plot underneath.
    """
    x_lim, t_lim, dx, dt, _ = field_pars

    z_limit = activity.max()
    contour_offset = activity.min() - 0.4

    x = np.arange(-x_lim, x_lim + dx, dx)
    t = np.arange(0, t_lim + dt, dt)

    x_mesh, t_mesh = np.meshgrid(x, t)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    surf = ax.plot_surface(t_mesh, x_mesh, activity, cmap=plt.get_cmap('plasma'),
                           linewidth=0, antialiased=False)
    ax.contourf(t_mesh, x_mesh, activity, zdir='z', offset=contour_offset, cmap='plasma')

    # Remove the gray shading
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    ax.set_box_aspect([2, 1, 1])

    fig.colorbar(surf, shrink=0.4, aspect=10, pad=0.2)

    ax.zaxis.set_rotate_label(False)

    ax.set_xlabel('t', linespacing=3.2)
    ax.set_ylabel('x', linespacing=3.1)
    ax.set_zlabel('u(x,t)', linespacing=3.4, rotation=0)

    ax.zaxis.labelpad = 10
    ax.set_zlim(contour_offset, z_limit)

    ax.set_yticks(np.arange(-x_lim, x_lim + dx, 2))

    plt.show()


def plot_time_courses(activity, field_pars, inputs, input_position):
    """
    Plot time courses of bump centers and inputs. Useful only when inputs are present.
    """
    x_lim, t_lim, dx, dt, theta = field_pars

    x = np.arange(-x_lim, x_lim + dx, dx)
    t = np.arange(0, t_lim + dt, dt)

    figure, ax = plt.subplots(figsize=(6, 4))

    if inputs.max() > 0:
        for i in range(np.shape(input_position)[0]):
            absolute_diff = np.abs(x - input_position[i])
            bump_center = np.argmin(absolute_diff)
            ax.plot(t, activity[:, bump_center])
            ax.plot(t, inputs[:, bump_center])
    else:
        ax.plot(t, activity[:, int(len(x) / 2)])

    ax.plot(t, theta * np.ones(np.shape(t)), label='theta', linestyle='dashed')
    ax.legend()
    plt.xlabel('x')
    plt.ylabel('u(x)', rotation=0, labelpad=15)
    ax.set_xlim(t[0], t[-1])
    plt.show()
