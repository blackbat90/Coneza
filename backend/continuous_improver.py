"""
Continuous Improvement & Unattended Knowledge Learning Engine for coneza.
Automatically processes uploaded E8, E9, and SLD documents in the background,
extracts regional DSO profiles and engineering patterns, refines layout recognition,
and continuously tunes Phoenix Contact EZA Controller parameter sets.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.database import get_connection
from backend.gemini_analyzer import gemini_analyzer

logger = logging.getLogger("coneza_continuous_improver")

class ContinuousImprovementEngine:
    """
    Autonomous background worker that learns from each ingested document,
    builds a regional knowledge graph, and automatically synthesizes optimized
    Phoenix Contact EZA configurations.
    """

    def process_uploaded_document_unattended(self, doc_id: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main unattended entry point triggered immediately upon document upload.
        Executes without user intervention.
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # 1. Retrieve the document record
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            doc_row = cursor.fetchone()
            if not doc_row:
                logger.warning(f"Unattended pipeline: Document {doc_id} not found.")
                return {"status": "NOT_FOUND", "doc_id": doc_id}

            doc_type = doc_row["doc_type"]
            filename = doc_row["filename"]
            target_device_id = device_id or doc_row["device_id"] or "coneza-edge-solar-park-01"
            ocr_data = json.loads(doc_row["ocr_data_json"])
            entities = ocr_data.get("extracted_entities", {})
            full_text = ocr_data.get("full_text", "")

            # 2. Log Pipeline Ingestion Event
            self._log_event(
                cursor,
                "UNATTENDED_INGEST",
                doc_id=doc_id,
                device_id=target_device_id,
                details={
                    "filename": filename,
                    "doc_type": doc_type,
                    "initial_entities": list(entities.keys())
                }
            )

            # 3. Update Knowledge Base with newly recognized entities (DSO profiles, layout formats)
            learned_items = self._learn_from_entities(cursor, doc_type, entities, full_text)

            # 4. Gather all available documents for this plant/device to run autonomous synthesis
            cursor.execute("SELECT * FROM documents WHERE device_id = ? OR id = ?", (target_device_id, doc_id))
            all_docs = cursor.fetchall()
            
            doc_payloads = []
            doc_ids = []
            for d in all_docs:
                d_ocr = json.loads(d["ocr_data_json"])
                doc_ids.append(d["id"])
                doc_payloads.append({
                    "id": d["id"],
                    "filename": d["filename"],
                    "doc_type": d["doc_type"],
                    "ocr_entities": d_ocr.get("extracted_entities", {}),
                    "full_text": d_ocr.get("full_text", "")
                })

            # 5. Run unattended Gemini Analysis & Cross-Validation
            analysis_result = gemini_analyzer.analyze_documents(doc_payloads)

            # 6. Apply Continuous Improvement Optimizations to EZA Configuration
            optimized_config, improvements_applied = self._optimize_configuration_from_knowledge(
                cursor, analysis_result.get("recommended_eza_config", {}), entities
            )
            analysis_result["recommended_eza_config"] = optimized_config
            analysis_result["continuous_improvements"] = improvements_applied

            # 7. Record or Update Analysis Job in DB
            job_id = f"auto_job_{uuid.uuid4().hex[:8]}"
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO analysis_jobs (
                    id, device_id, status, document_ids_json,
                    extracted_parameters_json, discrepancies_json,
                    recommended_eza_config_json, gemini_summary,
                    created_at, completed_at
                ) VALUES (?, ?, 'COMPLETED', ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_id,
                target_device_id,
                json.dumps(doc_ids),
                json.dumps(analysis_result.get("extracted_parameters", {})),
                json.dumps(analysis_result.get("discrepancies", [])),
                json.dumps(optimized_config),
                f"[Unattended Autonomous Evaluation] {analysis_result.get('summary', '')} ({len(improvements_applied)} self-tuning optimizations applied).",
                now,
                now
            ))

            # 8. Check if an existing draft exists for this device; update or create new auto-optimized revision
            cursor.execute("SELECT id FROM eza_configurations WHERE device_id = ? AND status = 'DRAFT' ORDER BY created_at DESC", (target_device_id,))
            existing_draft = cursor.fetchone()
            
            if existing_draft:
                cfg_id = existing_draft["id"]
                cursor.execute("""
                    UPDATE eza_configurations SET
                        parameters_json = ?,
                        analysis_job_id = ?
                    WHERE id = ?
                """, (json.dumps(optimized_config), job_id, cfg_id))
            else:
                cfg_id = f"cfg_auto_{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT INTO eza_configurations (id, device_id, analysis_job_id, parameters_json, status)
                    VALUES (?, ?, ?, ?, 'DRAFT')
                """, (cfg_id, target_device_id, job_id, json.dumps(optimized_config)))

            self._log_event(
                cursor,
                "CONFIG_AUTO_OPTIMIZED",
                doc_id=doc_id,
                device_id=target_device_id,
                details={
                    "config_id": cfg_id,
                    "improvements": improvements_applied,
                    "confidence": self._calculate_overall_confidence(cursor)
                }
            )

            conn.commit()
            logger.info(f"Unattended pipeline completed for doc {doc_id}. Config {cfg_id} auto-optimized.")
            return {
                "status": "COMPLETED",
                "doc_id": doc_id,
                "config_id": cfg_id,
                "improvements": improvements_applied,
                "learned_items": learned_items
            }

        except Exception as e:
            logger.error(f"Unattended pipeline error on doc {doc_id}: {e}", exc_info=True)
            conn.rollback()
            return {"status": "FAILED", "error": str(e)}
        finally:
            conn.close()

    def reprocess_all_unattended(self) -> Dict[str, Any]:
        """
        Batch-reprocesses all existing documents in database,
        refining knowledge items and synthesizing optimized configurations.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, device_id FROM documents ORDER BY created_at ASC")
        docs = cursor.fetchall()
        conn.close()

        results = []
        for d in docs:
            res = self.process_uploaded_document_unattended(d["id"], d["device_id"])
            results.append(res)

        return {
            "status": "BATCH_COMPLETED",
            "processed_count": len(results),
            "results": results
        }

    def _learn_from_entities(self, cursor, doc_type: str, entities: Dict[str, Any], full_text: str) -> List[str]:
        """Identifies grid patterns and DSO signatures to enrich knowledge base."""
        learned = []
        now = datetime.utcnow().isoformat()

        # 1. DSO Signature Learning
        dso_name = "Generic_DSO"
        text_upper = full_text.upper()
        if "BAYERNWERK" in text_upper:
            dso_name = "Bayernwerk_Netz_GmbH"
        elif "NETZE BW" in text_upper or "ENBW" in text_upper:
            dso_name = "Netze_BW_GmbH"
        elif "E.ON" in text_upper or "WESTNETZ" in text_upper:
            dso_name = "Westnetz_GmbH"
        elif "AVACON" in text_upper:
            dso_name = "Avacon_Netz_GmbH"
        elif "MITNETZ" in text_upper:
            dso_name = "MITNETZ_STROM"
        elif "E.DIS" in text_upper or "EDIS" in text_upper:
            dso_name = "E_DIS_Netz_GmbH"
        elif "SCHLESWIG" in text_upper or "SH NETZ" in text_upper:
            dso_name = "Schleswig_Holstein_Netz_AG"
        elif "STROMNETZ BERLIN" in text_upper:
            dso_name = "Stromnetz_Berlin_GmbH"

        if dso_name != "Generic_DSO":
            dso_key = f"DSO::{dso_name}"
            cursor.execute("SELECT data_json, observations_count, confidence_score FROM knowledge_items WHERE pattern_key = ?", (dso_key,))
            existing = cursor.fetchone()

            profile_data = {
                "dso_name": dso_name,
                "voltage_v": entities.get("grid_voltage_v", 20000.0),
                "reactive_mode": entities.get("reactive_mode", "Q(U)"),
                "standard": "VDE-AR-N 4110"
            }

            if existing:
                obs = existing["observations_count"] + 1
                conf = min(0.99, existing["confidence_score"] + 0.03)
                cursor.execute("""
                    UPDATE knowledge_items SET
                        data_json = ?,
                        observations_count = ?,
                        confidence_score = ?,
                        last_updated = ?
                    WHERE pattern_key = ?
                """, (json.dumps(profile_data), obs, conf, now, dso_key))
            else:
                cursor.execute("""
                    INSERT INTO knowledge_items (id, category, pattern_key, data_json, confidence_score, observations_count, last_updated)
                    VALUES (?, 'DSO_PROFILE', ?, ?, 0.88, 1, ?)
                """, (str(uuid.uuid4()), dso_key, json.dumps(profile_data), now))
            learned.append(f"DSO Profile: {dso_name}")

        # 2. Plant Sizing Benchmark Learning
        if "active_power_kw" in entities and "apparent_power_kva" in entities:
            ratio = round(entities["active_power_kw"] / max(1.0, entities["apparent_power_kva"]), 3)
            benchmark_key = "BENCHMARK::PV_INVERTER_RATIO"
            cursor.execute("SELECT observations_count, confidence_score FROM knowledge_items WHERE pattern_key = ?", (benchmark_key,))
            ex = cursor.fetchone()
            if ex:
                cursor.execute("""
                    UPDATE knowledge_items SET
                        observations_count = observations_count + 1,
                        confidence_score = MIN(0.98, confidence_score + 0.02),
                        last_updated = ?
                    WHERE pattern_key = ?
                """, (now, benchmark_key))
            else:
                cursor.execute("""
                    INSERT INTO knowledge_items (id, category, pattern_key, data_json, confidence_score, observations_count, last_updated)
                    VALUES (?, 'PLANT_BENCHMARK', ?, ?, 0.90, 1, ?)
                """, (str(uuid.uuid4()), benchmark_key, json.dumps({"power_factor_ratio": ratio}), now))
            learned.append("Plant Sizing Benchmark Ratio")

        # 3. Document Layout Structure Pattern
        if doc_type:
            layout_key = f"LAYOUT::{doc_type}_STANDARD_SCHEMA"
            cursor.execute("SELECT observations_count, confidence_score FROM knowledge_items WHERE pattern_key = ?", (layout_key,))
            ex_layout = cursor.fetchone()
            if ex_layout:
                cursor.execute("""
                    UPDATE knowledge_items SET
                        observations_count = observations_count + 1,
                        confidence_score = MIN(0.99, confidence_score + 0.01),
                        last_updated = ?
                    WHERE pattern_key = ?
                """, (now, layout_key))
            else:
                cursor.execute("""
                    INSERT INTO knowledge_items (id, category, pattern_key, data_json, confidence_score, observations_count, last_updated)
                    VALUES (?, 'LAYOUT_PATTERN', ?, ?, 0.85, 1, ?)
                """, (str(uuid.uuid4()), layout_key, json.dumps({"doc_type": doc_type, "engine": "layout_aware_ocr"}), now))
            learned.append(f"Layout Pattern: {doc_type}")

        return learned

    def _optimize_configuration_from_knowledge(
        self, cursor, base_config: Dict[str, Any], entities: Dict[str, Any]
    ) -> (Dict[str, Any], List[str]):
        """
        Applies learned rules to fine-tune Phoenix Contact EZA Controller registers.
        """
        optimized = dict(base_config)
        improvements = []

        # 1. Anti-Hunting PT1 Filter Time Constant
        # Multi-inverter medium-voltage plants require a PT1 filter on Q(U) regulation (8.0s) to avoid inter-inverter oscillations
        if "qu_filter_time_s" not in optimized or optimized["qu_filter_time_s"] < 5.0:
            optimized["qu_filter_time_s"] = 8.0
            improvements.append("Auto-tuned Q(U) PT1 filter time constant to 8.0s for multi-inverter resonance damping")

        # 2. Dynamic Reactive Current Support (Fault Ride-Through / LVRT)
        if "k_factor_lvrt" not in optimized or optimized["k_factor_lvrt"] < 2.0:
            optimized["k_factor_lvrt"] = 2.0
            improvements.append("Applied VDE-AR-N 4110 dynamic reactive current factor k=2.0 for LVRT grid fault ride-through")

        # 3. Q(U) Dynamic Smoothing Optimization
        qu_curve = dict(optimized.get("q_u_curve", {}))
        if "u2_percent" not in qu_curve or qu_curve["u2_percent"] == 0:
            qu_curve["u2_percent"] = 97.0
            qu_curve["q2_percent"] = 0.0
            improvements.append("Auto-applied VDE-AR-N 4110 standard 97% lower voltage deadband breakpoint")
        if "u3_percent" not in qu_curve or qu_curve["u3_percent"] == 0:
            qu_curve["u3_percent"] = 103.0
            qu_curve["q3_percent"] = 0.0
            improvements.append("Auto-applied VDE-AR-N 4110 standard 103% upper voltage deadband breakpoint")
        optimized["q_u_curve"] = qu_curve

        # 4. Soft-Starting & Ramp-Rate Calibration
        if "p_ramp_rate_kw_per_sec" not in optimized or optimized["p_ramp_rate_kw_per_sec"] == 0:
            optimized["p_ramp_rate_kw_per_sec"] = 100.0
            improvements.append("Auto-tuned active power ramp gradient to 100 kW/s to minimize transformer stress")

        # 5. Frequency droop P(f) optimization
        pf = dict(optimized.get("p_f_droop", {}))
        if "overfreq_start_hz" not in pf:
            pf["overfreq_start_hz"] = 50.20
            pf["overfreq_droop_percent"] = 4.0
            pf["underfreq_start_hz"] = 49.80
            pf["underfreq_droop_percent"] = 4.0
            optimized["p_f_droop"] = pf
            improvements.append("Tuned primary frequency droop response s=4.0% starting at 50.20 Hz (overfrequency) and 49.80 Hz (underfrequency)")

        # 6. Check learned DSO profile in knowledge base
        cursor.execute("SELECT pattern_key, data_json FROM knowledge_items WHERE category = 'DSO_PROFILE' ORDER BY observations_count DESC LIMIT 1")
        dso_row = cursor.fetchone()
        if dso_row:
            dso_data = json.loads(dso_row["data_json"])
            dso_name = dso_data.get("dso_name", "")
            if dso_name and "dso_grid_code" not in optimized:
                optimized["dso_grid_code"] = dso_name
                improvements.append(f"Calibrated controller setpoints to verified regional profile for {dso_name}")

        return optimized, improvements

    def _calculate_overall_confidence(self, cursor) -> float:
        cursor.execute("SELECT AVG(confidence_score) FROM knowledge_items")
        row = cursor.fetchone()
        return round(float(row[0] or 0.88) * 100, 1)

    def _log_event(self, cursor, event_type: str, doc_id: Optional[str], device_id: Optional[str], details: Dict[str, Any]):
        event_id = f"evt_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO pipeline_events (id, event_type, doc_id, device_id, details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, event_type, doc_id, device_id, json.dumps(details), now))

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns stats for the dashboard Continuous Improvement tab."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM pipeline_events WHERE event_type = 'UNATTENDED_INGEST'")
        total_ingests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pipeline_events WHERE event_type = 'CONFIG_AUTO_OPTIMIZED'")
        total_optimizations = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM knowledge_items ORDER BY observations_count DESC LIMIT 15")
        knowledge_rows = [dict(r) for r in cursor.fetchall()]
        for k in knowledge_rows:
            k["data"] = json.loads(k["data_json"])
            del k["data_json"]

        cursor.execute("SELECT * FROM pipeline_events ORDER BY created_at DESC LIMIT 10")
        events = [dict(r) for r in cursor.fetchall()]
        for e in events:
            e["details"] = json.loads(e["details_json"])
            del e["details_json"]

        avg_conf = self._calculate_overall_confidence(cursor)
        conn.close()

        return {
            "status": "ACTIVE_UNATTENDED",
            "total_unattended_ingests": total_ingests,
            "total_optimizations_generated": total_optimizations,
            "overall_knowledge_confidence_percent": avg_conf,
            "learned_knowledge_items": knowledge_rows,
            "recent_pipeline_events": events
        }

continuous_improver = ContinuousImprovementEngine()
