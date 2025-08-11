
#! python
import argparse
import datetime
import json

import os
import queue
import sys
import threading
from enum import IntFlag

from time import sleep, time

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.lines import Line2D

from radar import Radar
from radio_config import Radio_config
from spi.spi_Cheetah import SpiCheetah
from spi.spi_FTDI import SpiFTDI
from spi.spi_log import SpiLog

DEFAULT_SETTING_WINDOW = '{"device": "Dev0", "clock_rate": 15000000, ' \
                         '"idx_cir_start": 745, "idx_cir_end": 809, ' \
                         '"timer_clk_div": 7, "timer_period": 1666, ' \
                         '"run_time": 10, "frame_log_mode": 0}'

DEFAULT_SETTING_FIRST_PATH_CENTRIC = '{"device": "Dev0", "clock_rate": 15000000, ' \
                                     '"idx_cir_start": -8, "idx_cir_end": 56, ' \
                                     '"timer_clk_div": 7, "timer_period": 1333, ' \
                                     '"run_time": 10, "frame_log_mode": 1}'

q = queue.Queue()


class TimerClkDiv(IntFlag):
    DWT_XTAL = 0         # 38.4 MHz
    DWT_XTAL_DIV2 = 1    # 19.2 MHz
    DWT_XTAL_DIV4 = 2    # 9.6 MHz
    DWT_XTAL_DIV8 = 3    # 4.8 MHz
    DWT_XTAL_DIV16 = 4   # 2.4 MHz
    DWT_XTAL_DIV32 = 5   # 1.2 MHz
    DWT_XTAL_DIV64 = 6   # 0.6 MHz
    DWT_XTAL_DIV128 = 7  # 0.3 MHz


class FrameLogMode(IntFlag):
    WINDOW = 0
    FIRST_PATH_CENTRIC = 1


class Radar_runner(threading.Thread):
    def __init__(self, spi_driver, device, clock_rate, idx_cir_start, idx_cir_end,
                 timer_clk_div, timer_period, frame_log_mode):
        super().__init__()
        self._radar = Radar(spi_driver, device, clock_rate, idx_cir_start, idx_cir_end,
                            timer_clk_div, timer_period, frame_log_mode)

        self.frame_size = idx_cir_end - idx_cir_start
        self.cfg = self._radar.get_config()
        self.stopped = False
        self.frames = {'Configuration': {'clock_rate': clock_rate, 'idx_cir_start': idx_cir_start,
                                         'idx_cir_end': idx_cir_end, 'timer_clk_div': timer_clk_div,
                                         'timer_period': timer_period,
                                         'frame_log_mode': frame_log_mode,
                                         'Radio Config': self.cfg},
                       'Frames': []
                       }
        self._radar.get_reg_dump('radar_before_config.regdump')

    def run(self) -> None:
        self._radar.get_reg_dump('radar_after_config.regdump')
        self._radar.start()
        print('Running...')
        nb_frames = 0
        start = time()
        while not self.stopped:
            entry = self._radar.get_CIR()
            if entry:
                nb_frames += 1
                self.frames['Frames'].append(entry)
                q.put(entry)
        self._radar.stop()
        stop = time()
        self._radar.get_reg_dump('radar_after_stop.regdump')
        print(f'{nb_frames} frames in {stop - start}s ({nb_frames/(stop-start)} fps)')

    def stop(self):
        print('Stopped...')
        self.stopped = True

    def get_config(self):
        return self._radar.get_config()

    def set_config(self, cfg: dict):
        self._radar.set_config(cfg)


def save_cir_data_to_txt_file(path_to_file: str, data: dict):
    data_str = "---Configuration---\n"
    for k, v in data['Configuration'].items():
        if k == 'Radio Config':
            data_str += "---Radio Configuration---\n"
            for _k, _v in v.items():
                data_str += f"{_k}: {str(_v)}\n"
        else:
            data_str += f"{k}: {str(v)}\n"
    for d in data['Frames']:
        entry_str = f"FRAME {d['Frame']} DATA\n"
        entry_str += f"Frame Ok Counter: {d['Frame Ok Counter']}\n"
        entry_str += f"Frame Error Counter: {d['Frame Error Counter']}\n"
        entry_str += "---Timestamps---\n"
        for k, v in d['Timestamps'].items():
            entry_str += f"{k}: {str(v)} "
        entry_str += f"\n---Ipatov CIR Readings---\n"\
                     f"Re={str(d['Ipatov CIR']['re'])}\n" \
                     f"Im={str(d['Ipatov CIR']['im'])}\n" \
                     f"Z={str(d['Ipatov CIR']['z'])}\n"
        for _i, s in enumerate(d['STS CIRS']):
            entry_str += f"---STS {_i} CIR Readings---\n" \
                        f"Re={str(s['re'])}\n" \
                        f"Im={str(s['im'])}\n" \
                        f"Z={str(s['z'])}\n"
        entry_str += "CIA Registers\n"
        for k, v in d['CIA Registers'].items():
            entry_str += f"{k}={str(v)}, "
        entry_str += "\n---CIA Diagnostics---\n"
        for k, v in d['CIA Diagnostics'].items():
            entry_str += f"{k}={str(v)}, "
        entry_str += "\n"
        data_str += entry_str

    with open(path_to_file, 'x') as f:
        f.write(data_str)


def save_cir_data_to_json_file(path_to_file: str, data: dict):
    with open(path_to_file, 'x') as f:
        json_data = json.dumps(data, indent=4)
        f.write(json_data)


def save_plot_cir_data(x: dict, output: str):

    plt.title('IPT CIR Samples')
    plt.xlabel('Slow Time')
    plt.ylabel('Amplitude')
    nb_taps = len(x['Frames'][0]['Ipatov CIR']['z'])
    # color
    evenly_spaced_interval = np.linspace(0, 1, nb_taps)
    colors = [cm.rainbow(x) for x in evenly_spaced_interval]

    for i in range(nb_taps):
        plt.plot([x['Frames'][k]['Ipatov CIR']['z'][i] for k in range(len(x['Frames']))],
                 color=colors[i])

    # save figure before showing it, as show() clears the figure.
    plt.savefig(f'{output}_cirs.png')
    plt.show()

    plt.clf()


class RadarAnimation:
    def __init__(self, size, ylim):
        self.fig, (self.ax, self.CIRax) = plt.subplots(1, 2, sharey=True, figsize=(14, 6))

        self.ax.set_ylim(ylim)
        self.window = 100
        self.ax.set_xlim(0, self.window)
        self.i = 0
        self.x = []
        self.to_draw = [[] for _ in range(size)]

        # color
        evenly_spaced_interval = np.linspace(0, 1, size)
        colors = [cm.rainbow(x) for x in evenly_spaced_interval]
        self.lines = [Line2D([0], [0], color=colors[i]) for i in range(size)]

        for line in self.lines:
            self.ax.add_line(line)

        self.CIRline, = self.CIRax.plot([0.0]*size)

    def animate(self, frame_number):
        while q.qsize():
            frame = q.get()
            self.CIRline.set_ydata(frame['Ipatov CIR']['z'])
            self.x.append(self.i)

            for j, line in enumerate(self.lines):
                tmp = frame['Ipatov CIR']['z'][j]
                self.to_draw[j].append(tmp)
                line.set_data(self.x, self.to_draw[j])

            self.i = self.i+1
            if self.i > self.window:
                for d in self.to_draw:
                    d.pop(0)
                self.x.pop(0)
                self.ax.set_xlim(self.i-self.window, self.i)
        return self.lines + [self.CIRline]


def main():
    parser = argparse.ArgumentParser(description="""Capture, save and optionally plot CIR data.""")
    parser.add_argument("-i", "--interface", help="Set interface. spiftdi (default) or spicheetah",
                        default="spiftdi")
    parser.add_argument("-c", "--com", help="UART port. COM16 (default)", default="COM16")
    parser.add_argument("-o", "--output", help="Path to saved data", default="../Output")
    parser.add_argument("-p", "--plot", help="Plot the CIR, static (default) or live",
                        default="static")
    parser.add_argument("-s", "--settings",
                        help='Radar settings JSON object file',
                        default=None)
    parser.add_argument("-l", "--logspi", action='store_true',
                        help='Log all the SPI transactions on the bus.')
    args = parser.parse_args()

    frames = None
    log_name = f"Accumulator Log {datetime.datetime.now().strftime('%y-%m-%d-%Hh%Mm%Ss')}"
    if args.logspi:
        spi_log_name = f"spi-{datetime.datetime.now().strftime('%y-%m-%d-%Hh%Mm%Ss')}.log"
        spi_logger = SpiLog(spi_log_name)
    else:
        spi_logger = None

    if args.interface in ['spiftdi', 'spicheetah']:
        try:
            if(args.settings):
                with open(args.settings, 'r') as f:
                    radar_settings = json.load(f)
            else:
                radar_settings = json.loads(DEFAULT_SETTING_WINDOW)
            if args.plot == 'live':
                # override the timer_period to force realtime plot without loosing frames.
                radar_settings['timer_period'] = 7500
                print("Live plot enabled: forcing timer periode to "
                      f"{radar_settings['timer_period']} to guarantee synchronization between "
                      "frame acquisition and display.")
            print(radar_settings)
        except Exception as e:
            print(f"Invalid Radar Settings.\n{e}")
            radar_settings = None
        if radar_settings:
            try:
                if args.interface == "spicheetah":
                    driver = SpiCheetah(spi_logger)
                    print("Using Cheetah SPI to USB interface")
                else:
                    driver = SpiFTDI(spi_logger)
                    print("Using FTDI SPI to USB interface")
                rad = Radar_runner(spi_driver=driver, device=radar_settings['device'],
                                   clock_rate=radar_settings['clock_rate'],
                                   idx_cir_start=radar_settings['idx_cir_start'],
                                   idx_cir_end=radar_settings['idx_cir_end'],
                                   timer_clk_div=radar_settings['timer_clk_div'],
                                   timer_period=radar_settings['timer_period'],
                                   frame_log_mode=radar_settings['frame_log_mode'])
                if 'Radio Config' in radar_settings:
                    rad.set_config(radar_settings['Radio Config'])
                    # Verify the configuration
                    cfg = rad.get_config()
                    if Radio_config(radar_settings['Radio Config']) != Radio_config(cfg):
                        print("Error setting radio configuration !")
                        print(f"Config to set: {radar_settings['Radio Config']}")
                        print(f"Config in the QM35: {cfg}")
                        exit(-1)
                    # Update the configuration
                    rad.frames['Configuration']['Radio Config'] = cfg

                rad.start()
                if args.plot == 'live':
                    rad_ani = RadarAnimation(rad.frame_size, [0, 100000])
                    ani = animation.FuncAnimation(rad_ani.fig, rad_ani.animate, interval=1,
                                                  save_count=1, blit=True, cache_frame_data=False)
                    plt.show()
                else:
                    ani = None
                    sleep(radar_settings['run_time'])
                rad.stop()
                rad.join()
                frames = rad.frames
            except KeyboardInterrupt:
                print('Interrupted')
                if rad:
                    rad.stop()
                    rad.join()
                    frames = rad.frames
                    # Save CIR data
                    save_cir_data_to_json_file(f'{args.output}/{log_name}.json', frames)
                    save_cir_data_to_txt_file(f'{args.output}/{log_name}.txt', frames)
                if ani:
                    ani.event_source.stop()
                try:
                    sys.exit(0)
                except Exception:
                    os._exit(0)
    if frames:
        # Save CIR data
        save_cir_data_to_json_file(f'{args.output}/{log_name}.json', frames)
        save_cir_data_to_txt_file(f'{args.output}/{log_name}.txt', frames)
        # Optionally plot CIR data
        if args.plot == 'static':
            save_plot_cir_data(frames, f'{args.output}/{log_name}')
            pass


if __name__ == "__main__":
    main()
