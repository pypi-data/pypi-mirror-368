"""Main file for HTCFile object. Modified from WETB code.
"""
from collections import OrderedDict
import os
# from pathlib import Path

from lacbox.htc.os_path import fixcase, abspath, pjoin
from lacbox.htc.htc_contents import HTCContents, HTCSection, HTCLine
from lacbox.htc.htc_extensions import HTCDefaults, HTCExtensions


class HTCFile(HTCContents, HTCDefaults, HTCExtensions):
    """Load, manipulate and save HTC files.
    
    Parameters
    ----------
    filename : str or pathlib.Path
        Absolute filename of htc file
    modelpath : str or pathlib.Path
        Model path relative to htc file

    """

    filename = None
    htc_inputfiles = []
    level = 0
    modelpath = "../"
    initial_comments = None

    def __init__(self, filename=None, modelpath=None):
        """Initialization call."""
        # if filename is given, 
        if filename is not None:
            filename = str(filename)
            try:
                filename = fixcase(abspath(filename))
                with self.open(filename):
                    pass
            except Exception:
                pass

            self.filename = filename

        self.modelpath = str(modelpath) or self.auto_detect_modelpath()

        if filename and self.modelpath != "unknown" and not os.path.isabs(self.modelpath):
            drive, p = os.path.splitdrive(os.path.join(os.path.dirname(str(self.filename)), self.modelpath))
            self.modelpath = os.path.join(drive, os.path.splitdrive(os.path.realpath(p))[1]).replace("\\", "/")
        if self.modelpath != 'unknown' and self.modelpath[-1] != '/':
            self.modelpath += "/"

        self.load()

    def auto_detect_modelpath(self):
        if self.filename is None:
            return "../"

        #print (["../"*i for i in range(3)])
        import numpy as np
        input_files = HTCFile(self.filename, 'unknown').input_files()
        if len(input_files) == 1:  # only input file is the htc file
            return "../"
        rel_input_files = [f for f in input_files if not os.path.isabs(f)]

        def isfile_case_insensitive(f):
            try:
                f = fixcase(f)  # raises exception if not existing
                return os.path.isfile(f)
            except IOError:
                return False
        found = ([np.sum([isfile_case_insensitive(os.path.join(os.path.dirname(self.filename), "../" * i, f))
                          for f in rel_input_files]) for i in range(4)])

        if max(found) > 0:
            relpath = "../" * np.argmax(found)
            return abspath(pjoin(os.path.dirname(self.filename), relpath))
        else:
            raise ValueError(
                "Modelpath cannot be autodetected for '%s'.\nInput files not found near htc file" % self.filename)

    def load(self):
        self.contents = OrderedDict()
        self.initial_comments = []
        self.htc_inputfiles = []
        if self.filename is None:
            lines = self.empty_htc.split("\n")
        else:
            lines = self.readlines(self.filename)

        lines = [l.strip() for l in lines]

        #lines = copy(self.lines)
        while lines:
            if lines[0].startswith(";"):
                self.initial_comments.append(lines.pop(0).strip() + "\n")
            elif lines[0].lower().startswith("begin"):
                self._add_contents(HTCSection.from_lines(lines))
            else:
                line = HTCLine.from_lines(lines)
                if line.name_ == "exit":
                    break
                self._add_contents(line)

    def readfilelines(self, filename):
        with self.open(self.unix_path(os.path.abspath(filename.replace('\\', '/'))), encoding='cp1252') as fid:
            txt = fid.read()
        if txt[:10].encode().startswith(b'\xc3\xaf\xc2\xbb\xc2\xbf'):
            txt = txt[3:]
        return txt.replace("\r", "").split("\n")

    def readlines(self, filename):
        if filename != self.filename:  # self.filename may be changed by set_name/save. Added it when needed instead
            self.htc_inputfiles.append(filename)
        htc_lines = []
        lines = self.readfilelines(filename)
        for l in lines:
            if l.lower().lstrip().startswith('continue_in_file'):
                filename = l.lstrip().split(";")[0][len("continue_in_file"):].strip().lower()

                if self.modelpath == 'unknown':
                    p = os.path.dirname(self.filename)
                    lu = [os.path.isfile(os.path.abspath(os.path.join(p, "../" * i, filename.replace("\\", "/"))))
                          for i in range(4)].index(True)
                    filename = os.path.join(p, "../" * lu, filename)
                else:
                    filename = os.path.join(self.modelpath, filename)
                for line in self.readlines(filename):
                    if line.lstrip().lower().startswith('exit'):
                        break
                    htc_lines.append(line)
            else:
                htc_lines.append(l)
        return htc_lines

    def __setitem__(self, key, value):
        self.contents[key] = value

    def __str__(self):
        self.contents  # load
        return "".join(self.initial_comments + [c.__str__(1) for c in self] + ["exit;"])

    def save(self, filename=None):
        """Save the values in the htc object to an htc file.        

        Parameters
        ----------
        filename : str or pathlib.Path, optional
            Path to file to be saved. The default is None, in which case the filename is
            taken from the `HTCFile.filename` attribute.
        """
        self.contents  # load if not loaded
        if filename is None:
            filename = self.filename
        else:
            filename = str(filename)
            self.filename = filename
        # exist_ok does not exist in Python27
        if not os.path.exists(os.path.dirname(filename)) and os.path.dirname(filename) != "":
            os.makedirs(os.path.dirname(filename))  # , exist_ok=True)
        with self.open(filename, 'w', encoding='cp1252') as fid:
            fid.write(str(self))

    def set_name(self, name, logdir='log', resdir='res', htcdir='htc', subfolder=''):
        """Update the name of the file in the log, res, etc., fields.

        Parameters
        ----------
        name : str
            The name of the log file, dat file (for animation), hdf5 file
            (for visualization) and htc file.
        resdir : str, optional
            Name of model-level folder to save results files. The default is 'res'.
        htcdir : str, optional
            Name of model-level folder with htc files. The default is 'htc'.
        logdir : str, optional
            Name of model-level folder to save log files. The default is 'log'.
        subfolder : str, optional
            If you want your files to be placed in nested folders. For example, if
            subfolder is `cat`, then your htc files would be in `htc/cat/`, log files in
            `log/cat/`, etc. Can be useful when running different load cases. The default
            is '' (no subfolder).
        """
        # if os.path.isabs(folder) is False and os.path.relpath(folder).startswith("htc" + os.path.sep):
        self.contents  # load if not loaded

        def fmt_folder(folder, subfolder): return "./" + \
            os.path.relpath(os.path.join(folder, subfolder)).replace("\\", "/")

        self.filename = os.path.abspath(os.path.join(self.modelpath, fmt_folder(htcdir, subfolder), "%s.htc" % name)).replace("\\", "/")
        if 'simulation' in self and 'logfile' in self.simulation:
            self.simulation.logfile = os.path.join(fmt_folder(logdir, subfolder), "%s.log" % name).replace("\\", "/")
            if 'animation' in self.simulation:
                self.simulation.animation = os.path.join(fmt_folder(
                    'animation', subfolder), "%s.dat" % name).replace("\\", "/")
            if 'visualization' in self.simulation:
                f = os.path.join(fmt_folder('visualization', subfolder), "%s.hdf5" % name).replace("\\", "/")
                self.simulation.visualization[0] = f
        elif 'test_structure' in self and 'logfile' in self.test_structure:  # hawc2aero
            self.test_structure.logfile = os.path.join(fmt_folder(logdir, subfolder), "%s.log" % name).replace("\\", "/")
        if 'output' in self:
            self.output.filename = os.path.join(fmt_folder(resdir, subfolder), "%s" % name).replace("\\", "/")

    def set_time(self, start=None, stop=None, step=None):
        """Update simulation time in htc file.

        Args:
            start (int/float, optional): Time to start saving data to
                file. Defaults to None, i.e., keep current value in
                file.
            stop (int/float, optional): Time to stop saving data to
                file. Defaults to None, i.e., keep current value in
                file.
            step (int/float, optional): Time step. Defaults to None,
                i.e., keep current value in file.
        """
        self.contents  # load if not loaded
        if stop is not None:
            self.simulation.time_stop = stop
        else:
            stop = self.simulation.time_stop[0]
        if step is not None:
            self.simulation.newmark.deltat = step
        if start is not None:
            self.output.time = start, stop
            if "wind" in self:  # and self.wind.turb_format[0] > 0:
                self.wind.scale_time_start = start

    def expected_simulation_time(self):
        return 600

    def input_files(self):
        self.contents  # load if not loaded
        if self.modelpath == "unknown":
            files = [str(f).replace("\\", "/") for f in [self.filename] + self.htc_inputfiles]
        else:
            files = [os.path.abspath(str(f)).replace("\\", "/") for f in [self.filename] + self.htc_inputfiles]
        if 'new_htc_structure' in self:
            for mb in [self.new_htc_structure[mb]
                       for mb in self.new_htc_structure.keys() if mb.startswith('main_body')]:
                if "timoschenko_input" in mb:
                    files.append(mb.timoschenko_input.filename[0])
                files.append(mb.get('external_bladedata_dll', [None, None, None])[2])
        if 'aero' in self:
            files.append(self.aero.ae_filename[0])
            files.append(self.aero.pc_filename[0])
            files.append(self.aero.get('external_bladedata_dll', [None, None, None])[2])
            files.append(self.aero.get('output_profile_coef_filename', [None])[0])
            if 'dynstall_ateflap' in self.aero:
                files.append(self.aero.dynstall_ateflap.get('flap', [None] * 3)[2])
            if 'bemwake_method' in self.aero:
                files.append(self.aero.bemwake_method.get('a-ct-filename', [None] * 3)[0])
        for dll in [self.dll[dll] for dll in self.get('dll', {}).keys() if 'filename' in self.dll[dll]]:
            files.append(dll.filename[0])
            f, ext = os.path.splitext(dll.filename[0])
            files.append(f + "_64" + ext)
        if 'wind' in self:
            files.append(self.wind.get('user_defined_shear', [None])[0])
            files.append(self.wind.get('user_defined_shear_turbulence', [None])[0])
            files.append(self.wind.get('met_mast_wind', [None])[0])
        if 'wakes' in self:
            files.append(self.wind.get('use_specific_deficit_file', [None])[0])
            files.append(self.wind.get('write_ct_cq_file', [None])[0])
            files.append(self.wind.get('write_final_deficits', [None])[0])
        if 'hydro' in self:
            if 'water_properties' in self.hydro:
                files.append(self.hydro.water_properties.get('water_kinematics_dll', [None])[0])
                files.append(self.hydro.water_properties.get('water_kinematics_dll', [None, None])[1])
        if 'soil' in self:
            if 'soil_element' in self.soil:
                files.append(self.soil.soil_element.get('datafile', [None])[0])
        try:
            dtu_we_controller = self.dll.get_subsection_by_name('dtu_we_controller')
            theta_min = dtu_we_controller.init.constant__5[1]
            if theta_min >= 90:
                files.append(os.path.join(os.path.dirname(
                    dtu_we_controller.filename[0]), "wpdata.%d" % theta_min).replace("\\", "/"))
        except Exception:
            pass

        try:
            files.append(self.force.dll.dll[0])
        except Exception:
            pass

        def fix_path_case(f):
            if os.path.isabs(f):
                return self.unix_path(f)
            elif self.modelpath != "unknown":
                try:
                    return "./" + os.path.relpath(self.unix_path(os.path.join(self.modelpath, f)),
                                                  self.modelpath).replace("\\", "/")
                except IOError:
                    return f
            else:
                return f
        return [fix_path_case(f) for f in set(files) if f]

    def output_files(self):
        self.contents  # load if not loaded
        files = []
        for k, index in [('simulation/logfile', 0),
                         ('simulation/animation', 0),
                         ('simulation/visualization', 0),
                         ('new_htc_structure/beam_output_file_name', 0),
                         ('new_htc_structure/body_output_file_name', 0),
                         ('new_htc_structure/struct_inertia_output_file_name', 0),
                         ('new_htc_structure/body_eigenanalysis_file_name', 0),
                         ('new_htc_structure/constraint_output_file_name', 0),
                         ('wind/turb_export/filename_u', 0),
                         ('wind/turb_export/filename_v', 0),
                         ('wind/turb_export/filename_w', 0)]:
            line = self.get(k)
            if line:
                files.append(line[index])
        if 'new_htc_structure' in self:
            if 'system_eigenanalysis' in self.new_htc_structure:
                f = self.new_htc_structure.system_eigenanalysis[0]
                files.append(f)
                files.append(os.path.join(os.path.dirname(f), 'mode*.dat').replace("\\", "/"))
            if 'structure_eigenanalysis_file_name' in self.new_htc_structure:
                f = self.new_htc_structure.structure_eigenanalysis_file_name[0]
                files.append(f)
                files.append(os.path.join(os.path.dirname(f), 'mode*.dat').replace("\\", "/"))
        files.extend(self.res_file_lst())

        for key in [k for k in self.contents.keys() if k.startswith("output_at_time")]:
            files.append(self[key]['filename'][0] + ".dat")
        return [f.lower() for f in files if f]

    def turbulence_files(self):
        self.contents  # load if not loaded
        if 'wind' not in self.contents.keys() or self.wind.turb_format[0] == 0:
            return []
        elif self.wind.turb_format[0] == 1:
            files = [self.get('wind.mann.filename_%s' % comp, [None])[0] for comp in ['u', 'v', 'w']]
        elif self.wind.turb_format[0] == 2:
            files = [self.get('wind.flex.filename_%s' % comp, [None])[0] for comp in ['u', 'v', 'w']]
        return [f for f in files if f]

    def res_file_lst(self):
        self.contents  # load if not loaded
        res = []
        for output in [self[k] for k in self.keys()
                       if self[k].name_.startswith("output") and not self[k].name_.startswith("output_at_time")]:
            dataformat = output.get('data_format', 'hawc_ascii')
            res_filename = output.filename[0]
            if dataformat[0] == "gtsdf" or dataformat[0] == "gtsdf64":
                res.append(res_filename + ".hdf5")
            elif dataformat[0] == "flex_int":
                res.extend([res_filename + ".int", os.path.join(os.path.dirname(res_filename), 'sensor')])
            else:
                res.extend([res_filename + ".sel", res_filename + ".dat"])
        return res

    @property
    def open(self):
        return open

    def unix_path(self, filename):
        filename = os.path.realpath(str(filename)).replace("\\", "/")
        if not os.path.exists(filename):
            raise IOError(f'{filename} does not exist!')
        ufn, rest = os.path.splitdrive(filename)
        ufn += "/"
        for f in rest[1:].split("/"):
            f_lst = [f_ for f_ in os.listdir(ufn) if f_.lower() == f.lower()]
            if len(f_lst) > 1:
                # use the case sensitive match
                f_lst = [f_ for f_ in f_lst if f_ == f]
            if len(f_lst) == 0:
                raise IOError("'%s' not found in '%s'" % (f, ufn))
            else:  # one match found
                ufn = os.path.join(ufn, f_lst[0])
        return ufn.replace("\\", "/")




if __name__ == '__main__':
    f = HTCFile(r"C:\mmpe\HAWC2\models\DTU10MWRef6.0\htc\DTU_10MW_RWT_power_curve.htc", "../")
    print(f.input_files())
#     f.save(r"C:\mmpe\HAWC2\models\DTU10MWRef6.0\htc\DTU_10MW_RWT_power_curve.htc")
#
#     f = HTCFile(r"C:\mmpe\HAWC2\models\DTU10MWRef6.0\htc\DTU_10MW_RWT.htc", "../")
#     f.set_time = 0, 1, .1
#     print(f.simulate(r"C:\mmpe\HAWC2\bin\HAWC2_12.8\hawc2mb.exe"))
#
#     f.save(r"C:\mmpe\HAWC2\models\DTU10MWRef6.0\htc\DTU_10MW_RWT.htc")
