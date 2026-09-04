-- SafeSlope-NER Production Corridor Seed Script

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-128-Sonapur', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.846 25.547, 91.854 25.547, 91.854 25.553, 91.846 25.553, 91.846 25.547))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'HIGH', 'ensemble_model',
            1, 78.4, 91.2, 1.08,
            42.0, 185.0, -22.5,
            0.68, TRUE, FALSE,
            '[{"factor": "Antecedent Precipitation Index (40d)", "weight_pct": 38.0, "value": 185.0}, {"factor": "Mohr-Coulomb Factor of Safety Deficit", "weight_pct": 34.0, "value": 1.08}, {"factor": "InSAR Continuous Creep Rate", "weight_pct": 28.0, "value": -22.5}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-134-Umling', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.876 25.577, 91.884 25.577, 91.884 25.583, 91.876 25.583, 91.876 25.577))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'MODERATE', 'ensemble_model',
            1, 46.2, 88.5, 1.34,
            18.0, 110.0, -8.1,
            0.72, FALSE, FALSE,
            '[{"factor": "Rainfall Intensity", "weight_pct": 45.0, "value": 18.0}, {"factor": "Soil Saturation Index", "weight_pct": 35.0, "value": 0.65}, {"factor": "Topographic Slope Angle", "weight_pct": 20.0, "value": 36.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-06-KM-142-Ratacherra', 'NH-06-MEGHALAYA', '272', '17',
            ST_GeomFromText('POLYGON((91.916 25.617, 91.924 25.617, 91.924 25.623, 91.916 25.623, 91.916 25.617))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'CRITICAL', 'physics_floor',
            1, 94.8, 95.0, 0.82,
            68.5, 240.0, -48.2,
            0.55, TRUE, TRUE,
            '[{"factor": "Mohr-Coulomb FoS Breached (<1.0)", "weight_pct": 52.0, "value": 0.82}, {"factor": "Excess Pore-Water Pressure", "weight_pct": 30.0, "value": 38.5}, {"factor": "Anthropogenic Toe-Cut Overburden", "weight_pct": 18.0, "value": 1.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-54-KM-38-42-Sairang', 'NH-54-MIZORAM', '283', '15',
            ST_GeomFromText('POLYGON((92.645 23.776, 92.655 23.776, 92.655 23.784, 92.645 23.784, 92.645 23.776))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'HIGH', 'ensemble_model',
            2, 72.0, 82.0, 1.12,
            35.0, 190.0, -16.0,
            0.28, FALSE, FALSE,
            '[{"factor": "InSAR Blind Tier 2 GWaveNet Stress", "weight_pct": 40.0, "value": 0.72}, {"factor": "Soil Volumetric Water Content", "weight_pct": 35.0, "value": 74.0}, {"factor": "Acoustic Micro-Fracture AE Rate", "weight_pct": 25.0, "value": 18.0}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

        INSERT INTO risk_zones (
            zone_name, corridor_code, lgd_district_code, lgd_state_code,
            boundary, h3_r9_cells, h3_r10_cells, current_risk, risk_source,
            operational_tier, ml_risk_pct, ml_confidence_pct, fos_value,
            rainfall_intensity_mmhr, antecedent_precip_40d, insar_velocity_mmyr,
            insar_coherence, culvert_clogged, sentinel2_toe_cut, shap_drivers
        ) VALUES (
            'NH-54-KM-42-45-Thingdawl', 'NH-54-MIZORAM', '283', '15',
            ST_GeomFromText('POLYGON((92.675 23.816, 92.685 23.816, 92.685 23.824, 92.675 23.824, 92.675 23.816))', 4326),
            ARRAY['89003e6ec3e409']::TEXT[],
            ARRAY['8a003e6ec3e40a']::TEXT[],
            'LOW', 'ensemble_model',
            1, 14.5, 96.0, 1.85,
            4.0, 45.0, -2.1,
            0.78, FALSE, FALSE,
            '[{"factor": "High Factor of Safety (Stable)", "weight_pct": 70.0, "value": 1.85}, {"factor": "Low Pore Pressure", "weight_pct": 20.0, "value": 2.1}, {"factor": "Healthy Dense Root Cohesion", "weight_pct": 10.0, "value": 14.2}]'::JSONB
        ) ON CONFLICT (zone_name) DO UPDATE SET
            current_risk = EXCLUDED.current_risk,
            ml_risk_pct = EXCLUDED.ml_risk_pct,
            fos_value = EXCLUDED.fos_value,
            h3_r9_cells = EXCLUDED.h3_r9_cells,
            h3_r10_cells = EXCLUDED.h3_r10_cells
        RETURNING id;
        

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.847, 25.547), 4326),
                '89003e5ee3c609', '8a003e5ee3c60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.84819999999999, 25.5482), 4326),
                '89003e5fa3d109', '8a003e5fa3d10a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.84939999999999, 25.549400000000002), 4326),
                '89003e6e63dd09', '8a003e6e63dd0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.8506, 25.5506), 4326),
                '89003e6f23ea09', '8a003e6f23ea0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.8518, 25.5518), 4326),
                '89003e6fe3f609', '8a003e6fe3f60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-01-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.853, 25.553), 4326),
                '89003e6ea40209', '8a003e6ea4020a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.877, 25.576999999999998), 4326),
                '89003e7f94f209', '8a003e7f94f20a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.87819999999999, 25.5782), 4326),
                '89003e7e64fd09', '8a003e7e64fd0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.87939999999999, 25.5794), 4326),
                '89003e7f250909', '8a003e7f25090a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.8806, 25.580599999999997), 4326),
                '89003e7fd51609', '8a003e7fd5160a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.8818, 25.581799999999998), 4326),
                '89003e7e952209', '8a003e7e95220a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-02-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.883, 25.583), 4326),
                '89003e7f552e09', '8a003e7f552e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(91.917, 25.617), 4326),
                '89003e8ea68209', '8a003e8ea6820a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(91.9182, 25.6182), 4326),
                '89003e8f668e09', '8a003e8f668e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(91.9194, 25.619400000000002), 4326),
                '89003e8e269a09', '8a003e8e269a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(91.92060000000001, 25.6206), 4326),
                '89003e8ee6a609', '8a003e8ee6a60a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(91.9218, 25.6218), 4326),
                '89003e8fa6b209', '8a003e8fa6b20a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-03-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(91.923, 25.623), 4326),
                '89003e8e66be09', '8a003e8e66be0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(92.647, 23.777), 4326),
                '89003a0ea30609', '8a003a0ea3060a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(92.6482, 23.778200000000002), 4326),
                '89003a0f631209', '8a003a0f63120a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(92.6494, 23.779400000000003), 4326),
                '89003a0e231e09', '8a003a0e231e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(92.65060000000001, 23.7806), 4326),
                '89003a0ee32a09', '8a003a0ee32a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(92.65180000000001, 23.7818), 4326),
                '89003a0fa33609', '8a003a0fa3360a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-04-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(92.653, 23.783), 4326),
                '89003a1e634209', '8a003a1e63420a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-01', 'inclinometer', 101,
                ST_SetSRID(ST_MakePoint(92.677, 23.817), 4326),
                '89003a2fa43209', '8a003a2fa4320a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-02', 'geophone', 101,
                ST_SetSRID(ST_MakePoint(92.6782, 23.8182), 4326),
                '89003a2e643e09', '8a003a2e643e0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-03', 'ert', 101,
                ST_SetSRID(ST_MakePoint(92.6794, 23.8194), 4326),
                '89003a2f244a09', '8a003a2f244a0a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-04', 'rtk_gnss', 101,
                ST_SetSRID(ST_MakePoint(92.68060000000001, 23.8206), 4326),
                '89003a2fe45609', '8a003a2fe4560a', 0.05,
                TRUE, NULL
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-05', 'fbg', 101,
                ST_SetSRID(ST_MakePoint(92.68180000000001, 23.8218), 4326),
                '89003a2ea46209', '8a003a2ea4620a', 0.05,
                TRUE, '2026-09-13T19:36:36.765697+00:00'
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

            INSERT INTO sensors (
                sensor_id, sensor_type, gateway_id, location,
                corridor_h3_r9, corridor_h3_r10, installation_angle_offset,
                active_status, burn_in_expires_at
            ) VALUES (
                'NODE-05-06', 'turbidity', 101,
                ST_SetSRID(ST_MakePoint(92.683, 23.823), 4326),
                '89003a2f646e09', '8a003a2f646e0a', 0.05,
                TRUE, '2026-09-13T19:36:36.765697+00:00'
            ) ON CONFLICT (sensor_id) DO UPDATE SET
                corridor_h3_r9 = EXCLUDED.corridor_h3_r9,
                corridor_h3_r10 = EXCLUDED.corridor_h3_r10;
            

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Sonapur Village', '272001', '272', '17',
            ST_SetSRID(ST_MakePoint(91.849, 25.548), 4326),
            2001, 1450, 850,
            450, 6800.0, 1400.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(91.851, 25.5495), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Mawryngkneng Outpost', '272002', '272', '17',
            ST_SetSRID(ST_MakePoint(91.862, 25.556), 4326),
            2002, 2100, 1200,
            600, 9500.0, 2200.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(91.864, 25.557), 4326),
            0.3
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Umling Basti', '272003', '272', '17',
            ST_SetSRID(ST_MakePoint(91.881, 25.579), 4326),
            2003, 820, 450,
            250, 3200.0, 850.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(91.883, 25.582), 4326),
            0.5
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Ratacherra Border Hamlet', '272004', '272', '17',
            ST_SetSRID(ST_MakePoint(91.921, 25.619), 4326),
            2004, 650, 300,
            180, 1800.0, 450.0,
            1.3, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(91.923, 25.621), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Sairang Kawnpui', '283001', '283', '15',
            ST_SetSRID(ST_MakePoint(92.651, 23.781), 4326),
            2101, 3200, 1400,
            800, 14000.0, 3500.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(92.654, 23.783), 4326),
            0.6
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Thingdawl Veng', '283002', '283', '15',
            ST_SetSRID(ST_MakePoint(92.681, 23.821), 4326),
            2102, 1150, 550,
            300, 5200.0, 1100.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(92.683, 23.823), 4326),
            0.3
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Kolasib Junction', '283003', '283', '15',
            ST_SetSRID(ST_MakePoint(92.705, 23.845), 4326),
            2103, 4100, 1800,
            950, 18500.0, 4800.0,
            1.2, TRUE,
            TRUE, TRUE,
            ST_SetSRID(ST_MakePoint(92.708, 23.847), 4326),
            0.5
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO villages (
            village_name, lgd_village_code, lgd_district_code, lgd_state_code,
            location, graph_node_id, permanent_population, fastag_baseline_daily,
            resident_capacity_equivalent, pds_grain_stock_kg, pds_fuel_stock_litres,
            daily_consumption_burn_rate, has_primary_health_centre, has_school,
            has_pds_warehouse, nearest_helipad_location, nearest_helipad_dist_km
        ) VALUES (
            'Bilkhawthlir Valley', '283004', '283', '15',
            ST_SetSRID(ST_MakePoint(92.735, 23.865), 4326),
            2104, 980, 420,
            260, 4100.0, 900.0,
            1.2, FALSE,
            TRUE, FALSE,
            ST_SetSRID(ST_MakePoint(92.738, 23.867), 4326),
            0.4
        ) ON CONFLICT (lgd_village_code) DO UPDATE SET
            permanent_population = EXCLUDED.permanent_population,
            pds_grain_stock_kg = EXCLUDED.pds_grain_stock_kg;
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100000, 1001, 2001,
            ST_GeomFromText('LINESTRING(91.842 25.542, 91.849 25.548)', 4326),
            1, 'national_highway', 1850.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100001, 2001, 2002,
            ST_GeomFromText('LINESTRING(91.849 25.548, 91.854 25.552, 91.862 25.556)', 4326),
            1, 'national_highway', 2100.0,
            'BRIDGE', 8.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100002, 2002, 2003,
            ST_GeomFromText('LINESTRING(91.862 25.556, 91.872 25.568, 91.881 25.579)', 4326),
            2, 'national_highway', 3200.0,
            'NARROW_CUTTING', 1.8, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100003, 2003, 2004,
            ST_GeomFromText('LINESTRING(91.881 25.579, 91.902 25.601, 91.921 25.619)', 4326),
            3, 'national_highway', 4500.0,
            'CULVERT', 2.5, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100004, 2004, 1002,
            ST_GeomFromText('LINESTRING(91.921 25.619, 91.935 25.632)', 4326),
            3, 'national_highway', 2800.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100005, 2001, 3001,
            ST_GeomFromText('LINESTRING(91.849 25.548, 91.851 25.555)', 4326),
            1, 'village_road', 1200.0,
            'OPEN_ROAD', 1.0, FALSE,
            TRUE, TRUE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100006, 3001, 2002,
            ST_GeomFromText('LINESTRING(91.851 25.555, 91.862 25.556)', 4326),
            1, 'village_road', 1400.0,
            'OPEN_ROAD', 1.0, FALSE,
            TRUE, TRUE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100007, 2002, 3002,
            ST_GeomFromText('LINESTRING(91.862 25.556, 91.875 25.562, 91.89 25.572)', 4326),
            2, 'state_highway', 3800.0,
            'OPEN_ROAD', 1.0, FALSE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100008, 3002, 2003,
            ST_GeomFromText('LINESTRING(91.89 25.572, 91.881 25.579)', 4326),
            2, 'state_highway', 1900.0,
            'CULVERT', 2.5, FALSE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100009, 1101, 2101,
            ST_GeomFromText('LINESTRING(92.638 23.768, 92.651 23.781)', 4326),
            4, 'national_highway', 2400.0,
            'NARROW_CUTTING', 1.8, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100010, 2101, 2102,
            ST_GeomFromText('LINESTRING(92.651 23.781, 92.665 23.801, 92.681 23.821)', 4326),
            4, 'national_highway', 4100.0,
            'BRIDGE', 8.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100011, 2102, 2103,
            ST_GeomFromText('LINESTRING(92.681 23.821, 92.693 23.834, 92.705 23.845)', 4326),
            5, 'national_highway', 3600.0,
            'CULVERT', 2.5, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100012, 2103, 2104,
            ST_GeomFromText('LINESTRING(92.705 23.845, 92.72 23.856, 92.735 23.865)', 4326),
            5, 'national_highway', 2900.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        

        INSERT INTO road_edges (
            osm_id, u_node, v_node, geometry, associated_zone_id,
            highway_type, length_m, chokepoint_type,
            structural_duration_multiplier, is_strategic_defence,
            pedestrian_accessible, avoids_drainage_gully
        ) VALUES (
            100013, 2104, 1102,
            ST_GeomFromText('LINESTRING(92.735 23.865, 92.75 23.878)', 4326),
            5, 'national_highway', 3100.0,
            'OPEN_ROAD', 1.0, TRUE,
            FALSE, FALSE
        );
        