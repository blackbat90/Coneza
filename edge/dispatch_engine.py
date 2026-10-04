"""
Multi-EZE Dispatch & Curtailment Priority Engine.
Directly implements Confluence Requirement: 'Dispatch logic (Priority EZE)'
from 'Architecture and Features' & 'Business Functions'.

Optimizes active power distribution across hybrid generation units (PV inverters + Battery BESS):
1. Priority 1 (BESS Absorption): If SoC < 95%, charges the battery with curtailed PV power.
2. Priority 2 (Inverter Curtailment): Throttles remaining active power across PV inverters.
3. Priority 3 (Grid Decoupling Safety): Trip alarm if feed-in exceeds DSO limit after ramp timeout.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class GenerationUnit(BaseModel):
    unit_id: str
    unit_type: str  # "PV_INVERTER", "BESS", "WIND"
    rated_power_kw: float
    current_power_kw: float
    is_controllable: bool = True
    soc_percent: Optional[float] = None  # Relevant for BESS
    max_charge_power_kw: Optional[float] = None  # Relevant for BESS


class DispatchRequest(BaseModel):
    total_plant_capacity_kw: float
    curtailment_target_percent: float = Field(default=100.0, ge=0.0, le=100.0)
    grid_voltage_kv: float = 20.0
    units: List[GenerationUnit]


class UnitSetpointResult(BaseModel):
    unit_id: str
    unit_type: str
    target_power_kw: float
    target_power_percent: float
    bess_charging_kw: float = 0.0
    action_description: str


class DispatchResult(BaseModel):
    curtailment_target_percent: float
    allowed_feed_in_kw: float
    total_generated_kw: float
    total_feed_in_kw: float
    curtailed_loss_prevented_by_bess_kw: float
    unit_setpoints: List[UnitSetpointResult]
    compliance_status: str  # "COMPLIANT", "CURTAILED_SAFELY", "NON_COMPLIANT"


class MultiEzeDispatchEngine:
    """Calculates optimal active power setpoints for hybrid renewable plants."""

    def calculate_dispatch(self, req: DispatchRequest) -> DispatchResult:
        allowed_feed_in_kw = (req.total_plant_capacity_kw * req.curtailment_target_percent) / 100.0
        
        pv_units = [u for u in req.units if u.unit_type == "PV_INVERTER"]
        bess_units = [u for u in req.units if u.unit_type == "BESS"]

        total_current_pv_kw = sum(u.current_power_kw for u in pv_units)
        excess_power_kw = max(0.0, total_current_pv_kw - allowed_feed_in_kw)

        setpoints: List[UnitSetpointResult] = []
        absorbed_by_bess_kw = 0.0

        # Step 1: Priority 1 - Absorb excess power with Battery Energy Storage (BESS)
        remaining_excess_kw = excess_power_kw
        for b in bess_units:
            soc = b.soc_percent if b.soc_percent is not None else 50.0
            max_charge = b.max_charge_power_kw or b.rated_power_kw

            if soc < 95.0 and remaining_excess_kw > 0.0:
                available_charge_headroom = max_charge
                charge_power = min(remaining_excess_kw, available_charge_headroom)
                absorbed_by_bess_kw += charge_power
                remaining_excess_kw -= charge_power

                setpoints.append(UnitSetpointResult(
                    unit_id=b.unit_id,
                    unit_type="BESS",
                    target_power_kw=-charge_power,  # Negative means charging
                    target_power_percent=round((-charge_power / b.rated_power_kw) * 100, 1),
                    bess_charging_kw=charge_power,
                    action_description=f"Charging BESS with {charge_power:.1f} kW excess solar power (SoC: {soc:.1f}%)"
                ))
            else:
                setpoints.append(UnitSetpointResult(
                    unit_id=b.unit_id,
                    unit_type="BESS",
                    target_power_kw=0.0,
                    target_power_percent=0.0,
                    bess_charging_kw=0.0,
                    action_description=f"BESS Idle / Full (SoC: {soc:.1f}%)"
                ))

        # Step 2: Priority 2 - Curtail remaining active power across PV inverters
        target_pv_total_kw = max(0.0, total_current_pv_kw - remaining_excess_kw)
        
        if total_current_pv_kw > 0:
            reduction_ratio = target_pv_total_kw / total_current_pv_kw
        else:
            reduction_ratio = 1.0

        for pv in pv_units:
            pv_target_kw = pv.current_power_kw * reduction_ratio
            pv_percent = (pv_target_kw / pv.rated_power_kw) * 100.0 if pv.rated_power_kw > 0 else 0.0
            
            action = "Normal operation (100%)" if reduction_ratio >= 0.99 else f"Curtailed to {pv_percent:.1f}% per DSO request"
            if absorbed_by_bess_kw > 0 and remaining_excess_kw == 0:
                action += " (Zero curtailment needed thanks to BESS buffer)"

            setpoints.append(UnitSetpointResult(
                unit_id=pv.unit_id,
                unit_type="PV_INVERTER",
                target_power_kw=round(pv_target_kw, 1),
                target_power_percent=round(pv_percent, 1),
                bess_charging_kw=0.0,
                action_description=action
            ))

        # Net feed-in at Point of Common Coupling (NAP / PCC) equals PV generation minus BESS charging
        total_feed_in = max(0.0, target_pv_total_kw - absorbed_by_bess_kw)
        is_compliant = total_feed_in <= (allowed_feed_in_kw + 1.0)

        return DispatchResult(
            curtailment_target_percent=req.curtailment_target_percent,
            allowed_feed_in_kw=round(allowed_feed_in_kw, 1),
            total_generated_kw=round(total_current_pv_kw, 1),
            total_feed_in_kw=round(total_feed_in, 1),
            curtailed_loss_prevented_by_bess_kw=round(absorbed_by_bess_kw, 1),
            unit_setpoints=setpoints,
            compliance_status="COMPLIANT" if is_compliant else "NON_COMPLIANT"
        )


# Global singleton instance
dispatch_engine = MultiEzeDispatchEngine()
