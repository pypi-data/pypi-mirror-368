from typing import Union

__all__ = (
    "AmberParameters",
    "MinRestrainedParameters",
    "MDRestrainedParameters",
    "MDParameters",
    "HeatingParameters",
    "AnhilateParameters",
    "LambdaParameters",
)


class AmberParameters:
    def __init__(
        self,
        *,
        nstlim: int,
        dt: float = 0.002,
        irest: int = 1,
        ntx: int = 5,
        ntxo: int = 1,
        ntpr: int = 1000,
        ntwr: int = 500,
        ntwx: int = 0,
        iwrap: int = 0,
        ntc: int = 2,
        tol: float = 0.00001,
        ntf: int = 2,
        nscm: int = 1000,
        ntb: int = 1,
        ntp: int = 0,
        barostat: int = 2,
        mcbarint: int = 100,
        ntt: int = 3,
        gamma_ln: float = 5.0,
        temp0: int = 300,
        tempi: int = 300,
        ntr: int = 0,
        restraint_wt: float = 10.0,
        restraintmask: str = "@CA,N,C,O",
        nmropt: int = 0,
        istep1: int = 100,
        istep2: int = 300,
        value1: float = 100,
        value2: float = 100,
        cut: float = 9.0,
        maxcyc: int = 1000,
        ncyc: int = 100,
        ntmin: int = 1,
        ifsc: int = 1,
        icfe: int = 1,
        ifmbar: int = 1,
        numexchg: int = 0,
        bar_intervall: int = 125,
        timask1: str = ":1",
        timask2: str = "",
        crgmask: str = "",
        scmask1: str = ":1",
        scmask2: str = "",
        scalpha: float = 0.5,
        scbeta: float = 1.0,
        gti_cut: float = 1,
        gti_output: int = 1,
        gti_add_sc: int = 25,
        gti_scale_beta: int = 1,
        gti_cut_sc_on: int = 8,
        gti_cut_sc_off: int = 10,
        gti_lam_sch: int = 1,
        gti_ele_sc: int = 1,
        gti_vdw_sc: int = 1,
        gti_cut_sc: int = 2,
        gti_ele_exp: int = 2,
        gti_vdw_exp: int = 2,
        gti_syn_mass: int = 0,
        gremd_acyc: int = 1,
        gti_bat_sc: int = -1,
    ):
        """Initialize AmberInputParameters.

        Args:
            nstlim (int): Number of MD steps to be performed.
            dt (float, optional): Time step in picoseconds. Defaults to 0.002.
            irest (int, optional): Flag to restart simulation. 0 for no restart, 1 to restart. Defaults to 1.
            ntx (int, optional): Option to read coordinates and velocities. Defaults to 5.
            ntxo (int, optional): Format of the final coordinates written to restart file. Defaults to 1.
            ntpr (int, optional): Print energy information to mdout and mdinfo every N steps. Defaults to 50.
            ntwr (int, optional): Write restart file every N steps. Defaults to 500.
            ntwx (int, optional): Write coordinates to trajectory file every N steps. Defaults to 0.
            iwrap (int, optional): Option to wrap coordinates into primary box. Defaults to 0.
            ntc (int, optional): SHAKE settings. 0 for no SHAKE, 2 for only hydrogen bonds, 3 for all bonds. Defaults to 2.
            tol (float, optional): Tolerance for SHAKE algorithm. Defaults to 0.00001.
            ntf (int, optional): Number of forces to be calculated. Defaults to 2.
            nscm (int, optional): Option for center of mass motion removal. Defaults to 1000.
            ntb (int, optional): Option for periodic boundary conditions. 0 for no PBC, 1 for constant volume, 2 for constant pressure. Defaults to 1.
            ntp (int, optional): Option for pressure scaling. 0 for no scaling, 1 for isotropic, 2 for anisotropic. Defaults to 0.
            barostat (int, optional): Pressure regulation algorithm. 1 for Berendsen, 2 for Langevin. Defaults to 2.
            mcbarint (int, optional): Interval for Monte Carlo barostat attempts. Defaults to 100.
            ntt (int, optional): Thermostat option. 0 for no thermostat, 1 for Berendsen, 3 for Langevin. Defaults to 3.
            gamma_ln (float, optional): Collision frequency for Langevin thermostat (ps^-1). Defaults to 5.0.
            temp0 (int, optional): Target temperature in Kelvin. Defaults to 300.
            tempi (int, optional): Initial temperature in Kelvin. Defaults to 300.
            ntr (int, optional): Flag for using positional restraints. 0 for no restraints, 1 for restraints. Defaults to 0.
            restraint_wt (float, optional): Weight for positional restraints (kcal/mol/A^2). Defaults to 10.0.
            restraintmask (str, optional): Amber mask for atoms to be restrained. Defaults to '@CA,N,C,O'.
            nmropt (int, optional): Flag for NMR restraints and options. Defaults to 0.
            istep1 (int, optional): For nmropt > 0, step number for first change in target value. Defaults to 100.
            istep2 (int, optional): For nmropt > 0, step number for second change in target value. Defaults to 300.
            value1 (float, optional): For nmropt > 0, target value for first period. Defaults to 100.
            value2 (float, optional): For nmropt > 0, target value for second period. Defaults to 100.
            cut (float, optional): Nonbonded cutoff in Angstroms. Defaults to 9.0.
            maxcyc (int, optional): Maximum number of minimization cycles. Defaults to 1000.
            ncyc (int, optional): Number of steepest descent cycles before switching to conjugate gradient. Defaults to 100.
            ntmin (int, optional): Minimization method flag. Defaults to 1.
            ifsc (int, optional): Flag for soft-core potential. Defaults to 1.
            icfe (int, optional): Flag for free energy calculation. Defaults to 1.
            ifmbar (int, optional): Flag for MBAR analysis. Defaults to 1.
            numexchg (int, optional): Number of exchanges to perform, when doing REMD. Defaults to 0.
            bar_intervall (int, optional): Interval for BAR samples. Defaults to 0.
            timask1 (int, optional): First time mask selection. Defaults to ":1".
            timask2 (int, optional): Second time mask selection. Defaults to "".
            crgmask (int, optional): Charge mask selection. Defaults to "".
            scmask1 (int, optional): First soft-core mask selection. Defaults to ":1".
            scmask2 (int, optional): Second soft-core mask selection. Defaults to "".
            scalpha (int, optional): Soft-core alpha parameter. Defaults to 0.5.
            scbeta (int, optional): Soft-core beta parameter. Defaults to 1.0.
            gti_cut (int, optional): GTI cutoff flag. Defaults to 1.
            gti_output (int, optional): GTI output flag. Defaults to 1.
            gti_add_sc (int, optional): GTI soft-core addition steps. Defaults to 25.
            gti_scale_beta (int, optional): GTI beta scaling flag. Defaults to 1.
            gti_cut_sc_on (int, optional): GTI soft-core cutoff on value. Defaults to 8.
            gti_cut_sc_off (int, optional): GTI soft-core cutoff off value. Defaults to 10.
            gti_lam_sch (int, optional): GTI lambda schedule type. Defaults to 1.
            gti_ele_sc (int, optional): GTI electrostatic soft-core flag. Defaults to 1.
            gti_vdw_sc (int, optional): GTI van der Waals soft-core flag. Defaults to 1.
            gti_cut_sc (int, optional): GTI soft-core cutoff type. Defaults to 2.
            gti_ele_exp (int, optional): GTI electrostatic exponent. Defaults to 2.
            gti_vdw_exp (int, optional): GTI van der Waals exponent. Defaults to 2.
            gremd_acyc (int, optional): gREM/d acetyl cycles. Defaults to 1.
            gti_bat_sc (int, optional): GTI BAT soft-core flag. Defaults to -1.
        """
        for name, value in locals().items():
            if name != "self":
                setattr(self, name, value)

    def as_dict(self) -> dict[str, Union[str, int, float]]:
        return {str(k).upper(): v for k, v in self.__dict__.items() if v is not None}

    def __repr__(self) -> str:
        return f"AmberParameters({', '.join(f'{k}={v}' for k, v in self.as_dict().items())})"

    def __str__(self) -> str:
        return "\n".join(f"{k}={v}" for k, v in self.as_dict().items() if v is not None)


class MinRestrainedParameters(AmberParameters):
    def __init__(
        self,
        *,
        ntx: int = 1,
        ntxo: int = 1,
        ntpr: int = 1000,
        ntwr: int = 0,
        ntc: int = 2,
        tol: float = 0.00001,
        ntf: int = 2,
        ntb: int = 1,
        ntp: int = 0,
        ntr: int = 1,
        restraint_wt: float = 50.0,
        restraintmask: str = "@CA,N,C,O",
        cut: float = 9.0,
        maxcyc: int = 400,
        ncyc: int = 50,
        ntmin: int = 1,
    ):
        super().__init__(
            nstlim=0,
            ntx=ntx,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntc=ntc,
            tol=tol,
            ntf=ntf,
            ntb=ntb,
            ntp=ntp,
            ntr=ntr,
            restraint_wt=restraint_wt,
            restraintmask=restraintmask,
            cut=cut,
            maxcyc=maxcyc,
            ncyc=ncyc,
            ntmin=ntmin,
        )


class MDRestrainedParameters(AmberParameters):
    def __init__(
        self,
        *,
        nstlim: int,
        dt: float = 0.002,
        irest: int = 1,
        ntx: int = 5,
        ntxo: int = 1,
        ntpr: int = 1000,
        ntwr: int = 500,
        ntwx: int = 0,
        iwrap: int = 0,
        nscm: int = 0,
        ntb: int = 2,
        ntp: int = 1,
        barostat: int = 2,
        mcbarint: int = 100,
        ntt: int = 3,
        gamma_ln: float = 5.0,
        temp0: int = 298,
        restraint_wt: float = 50.0,
        restraintmask: str = "@CA,N,C,O",
        cut: float = 9.0,
    ):
        super().__init__(
            nstlim=nstlim,
            dt=dt,
            irest=irest,
            ntx=ntx,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntwx=ntwx,
            iwrap=iwrap,
            nscm=nscm,
            ntb=ntb,
            ntp=ntp,
            barostat=barostat,
            mcbarint=mcbarint,
            ntt=ntt,
            gamma_ln=gamma_ln,
            temp0=temp0,
            restraint_wt=restraint_wt,
            restraintmask=restraintmask,
            cut=cut,
        )


class MDParameters(AmberParameters):
    def __init__(
        self,
        *,
        nstlim: int,
        dt: float = 0.002,
        irest: int = 1,
        ntx: int = 5,
        ntxo: int = 1,
        ntpr: int = 1000,
        ntwr: int = 500,
        ntwx: int = 0,
        iwrap: int = 0,
        nscm: int = 0,
        ntb: int = 2,
        ntp: int = 1,
        barostat: int = 2,
        mcbarint: int = 100,
        ntt: int = 3,
        gamma_ln: float = 5.0,
        temp0: int = 298,
        cut: float = 9.0,
    ):
        super().__init__(
            nstlim=nstlim,
            dt=dt,
            irest=irest,
            ntx=ntx,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntwx=ntwx,
            iwrap=iwrap,
            nscm=nscm,
            ntb=ntb,
            ntp=ntp,
            barostat=barostat,
            mcbarint=mcbarint,
            ntt=ntt,
            gamma_ln=gamma_ln,
            temp0=temp0,
            cut=cut,
        )


class HeatingParameters(AmberParameters):
    def __init__(
        self,
        *,
        nstlim: int,
        dt: float = 0.001,
        ntxo: int = 1,
        ntpr: int = 250,
        ntwr: int = 250,
        temp0: int = 298,
        tempi: int = 100,
        ntr: int = 0,
        restraint_wt: float = 50.0,
        restraintmask: str = "@CA,N,C,O",
        nmropt: int = 0,
        cut: float = 9.0,
    ):
        super().__init__(
            nstlim=nstlim,
            dt=dt,
            irest=0,
            ntx=1,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntwx=250,
            iwrap=0,
            ntc=2,
            ntf=2,
            nscm=0,
            ntb=1,
            ntp=0,
            ntt=3,
            gamma_ln=1.0,
            temp0=temp0,
            tempi=tempi,
            ntr=ntr,
            restraint_wt=restraint_wt,
            restraintmask=restraintmask,
            nmropt=nmropt,
            istep1=0,
            istep2=nstlim,
            value1=tempi,
            value2=temp0,
            cut=cut,
        )


class AnhilateParameters(AmberParameters):
    def __init__(
        self,
        *,
        nstlim: int = 1,
        ntx: int = 1,
        ntxo: int = 1,
        ntpr: int = 1000,
        ntwr: int = 0,
        ntc: int = 2,
        tol: float = 0.00001,
        ntf: int = 2,
        cut: float = 10.0,
        maxcyc: int = 5000,
        ntmin: int = 2,
        ifsc: int = 1,
        icfe: int = 1,
        timask1: str = ":1",
        timask2: str = "",
        crgmask: str = "",
        scmask1: str = ":1",
        scmask2: str = "",
        scalpha: float = 0.5,
        scbeta: float = 1.0,
        gti_cut: float = 1,
        gti_output: int = 1,
        gti_add_sc: int = 25,
        gti_scale_beta: int = 1,
        gti_cut_sc: int = 2,
        gti_cut_sc_on: int = 8,
        gti_cut_sc_off: int = 10,
        gti_lam_sch: int = 1,
        gti_ele_sc: int = 1,
        gti_vdw_sc: int = 1,
        gti_ele_exp: int = 2,
        gti_vdw_exp: int = 2,
        gti_syn_mass: int = 0,
        gti_bat_sc: int = -1,
    ):
        super().__init__(
            nstlim=nstlim,
            ntx=ntx,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntc=ntc,
            tol=tol,
            ntf=ntf,
            cut=cut,
            maxcyc=maxcyc,
            ntmin=ntmin,
            ifsc=ifsc,
            icfe=icfe,
            timask1=timask1,
            timask2=timask2,
            crgmask=crgmask,
            scmask1=scmask1,
            scmask2=scmask2,
            scalpha=scalpha,
            scbeta=scbeta,
            gti_cut=gti_cut,
            gti_output=gti_output,
            gti_add_sc=gti_add_sc,
            gti_scale_beta=gti_scale_beta,
            gti_cut_sc=gti_cut_sc,
            gti_cut_sc_on=gti_cut_sc_on,
            gti_cut_sc_off=gti_cut_sc_off,
            gti_lam_sch=gti_lam_sch,
            gti_ele_sc=gti_ele_sc,
            gti_vdw_sc=gti_vdw_sc,
            gti_ele_exp=gti_ele_exp,
            gti_vdw_exp=gti_vdw_exp,
            gti_syn_mass=gti_syn_mass,
            gti_bat_sc=gti_bat_sc,
        )


class LambdaParameters(AmberParameters):
    def __init__(
        self,
        *,
        nstlim: int,
        dt: float = 0.002,
        irest: int = 1,
        ntx: int = 5,
        ntxo: int = 1,
        ntpr: int = 125,
        ntwr: int = 0,
        temp0: int = 298,
        tempi: int = 100,
        ntc: int = 2,
        tol: float = 0.00001,
        ntf: int = 2,
        cut: float = 10.0,
        maxcyc: int = 5000,
        ntmin: int = 2,
        ifsc: int = 1,
        icfe: int = 1,
        timask1: str = ":1",
        timask2: str = "",
        crgmask: str = "",
        scmask1: str = ":1",
        scmask2: str = "",
        numexchg: int = 10000,
        bar_intervall: int = 125,
        scalpha: float = 0.5,
        scbeta: float = 1.0,
        gti_cut: float = 1,
        gti_output: int = 1,
        gti_add_sc: int = 25,
        gti_scale_beta: int = 1,
        gti_cut_sc_on: int = 8,
        gti_cut_sc_off: int = 10,
        gti_lam_sch: int = 1,
        gti_ele_sc: int = 1,
        gti_vdw_sc: int = 1,
        gti_cut_sc: int = 2,
        gti_ele_exp: int = 2,
        gti_vdw_exp: int = 2,
        gti_syn_mass: int = 0,
        gremd_acyc: int = 1,
        gti_bat_sc: int = -1,
    ):
        super().__init__(
            nstlim=nstlim,
            dt=dt,
            irest=irest,
            ntx=ntx,
            ntxo=ntxo,
            ntpr=ntpr,
            ntwr=ntwr,
            ntc=ntc,
            tol=tol,
            ntf=ntf,
            cut=cut,
            maxcyc=maxcyc,
            ntmin=ntmin,
            temp0=temp0,
            tempi=tempi,
            istep1=0,
            istep2=nstlim,
            value1=tempi,
            value2=temp0,
            ifsc=ifsc,
            icfe=icfe,
            timask1=timask1,
            timask2=timask2,
            crgmask=crgmask,
            scmask1=scmask1,
            scmask2=scmask2,
            numexchg=numexchg,
            bar_intervall=bar_intervall,
            scalpha=scalpha,
            scbeta=scbeta,
            gti_cut=gti_cut,
            gti_output=gti_output,
            gti_add_sc=gti_add_sc,
            gti_scale_beta=gti_scale_beta,
            gti_cut_sc_on=gti_cut_sc_on,
            gti_cut_sc_off=gti_cut_sc_off,
            gti_lam_sch=gti_lam_sch,
            gti_ele_sc=gti_ele_sc,
            gti_vdw_sc=gti_vdw_sc,
            gti_cut_sc=gti_cut_sc,
            gti_ele_exp=gti_ele_exp,
            gti_vdw_exp=gti_vdw_exp,
            gti_syn_mass=gti_syn_mass,
            gremd_acyc=gremd_acyc,
            gti_bat_sc=gti_bat_sc,
        )
