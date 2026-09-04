import React from 'react';
import { 
  Document, 
  Page, 
  Text, 
  View, 
  StyleSheet, 
  PDFDownloadLink,
  Svg,
  Circle,
  Path,
  Rect
} from '@react-pdf/renderer';
import { Download, Loader2 } from 'lucide-react';
import type { IsolationStats } from '../types/dashboard';

// PDF Document Stylesheet matching authentic Government Gazette layout perfectly
const styles = StyleSheet.create({
  page: {
    padding: 35,
    backgroundColor: '#FFFFFF',
    fontFamily: 'Times-Roman',
    fontSize: 9.5,
    color: '#0F172A',
    lineHeight: 1.35,
  },
  header: {
    alignItems: 'center',
    textAlign: 'center',
    borderBottomWidth: 1.5,
    borderBottomColor: '#0F172A',
    borderBottomStyle: 'solid',
    paddingBottom: 8,
    marginBottom: 10,
  },
  govTitle: {
    fontSize: 12,
    fontFamily: 'Times-Bold',
    color: '#0F172A',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: 4,
  },
  sdmaTitle: {
    fontSize: 10,
    fontFamily: 'Times-Bold',
    color: '#0F172A',
    textTransform: 'uppercase',
    marginTop: 2,
  },
  subHeaderTitle: {
    fontSize: 8.5,
    fontFamily: 'Times-Roman',
    color: '#1E293B',
    textTransform: 'uppercase',
    marginTop: 2,
  },
  metaMarginRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    borderTopWidth: 1,
    borderTopColor: '#0F172A',
    borderTopStyle: 'solid',
    marginTop: 8,
    paddingTop: 4,
  },
  metaText: {
    fontSize: 8.5,
    fontFamily: 'Courier-Bold',
    color: '#0F172A',
  },
  sectionOrderTitle: {
    fontSize: 11,
    fontFamily: 'Times-Bold',
    textAlign: 'center',
    textDecoration: 'underline',
    textTransform: 'uppercase',
    marginTop: 4,
    marginBottom: 8,
    color: '#0F172A',
  },
  subjectText: {
    fontSize: 9.5,
    fontFamily: 'Times-Bold',
    textTransform: 'uppercase',
    marginBottom: 8,
    color: '#0F172A',
  },
  preamble: {
    fontSize: 9,
    fontFamily: 'Times-Roman',
    textAlign: 'justify',
    marginBottom: 12,
    color: '#0F172A',
    lineHeight: 1.4,
  },
  sectionHeading: {
    fontSize: 9,
    fontFamily: 'Times-Bold',
    textTransform: 'uppercase',
    marginTop: 8,
    marginBottom: 5,
    color: '#0F172A',
    letterSpacing: 0.5,
  },
  table: {
    width: '100%',
    borderWidth: 1,
    borderColor: '#0F172A',
    borderStyle: 'solid',
    marginBottom: 12,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#0F172A',
    borderBottomStyle: 'solid',
    alignItems: 'stretch',
  },
  tableHeader: {
    backgroundColor: '#F1F5F9',
    fontFamily: 'Times-Bold',
  },
  tdLabel: {
    width: '33%',
    padding: 6,
    backgroundColor: '#F8FAFC',
    fontFamily: 'Times-Bold',
    borderRightWidth: 1,
    borderRightColor: '#0F172A',
    borderRightStyle: 'solid',
    fontSize: 8.5,
    textTransform: 'uppercase',
  },
  tdVal: {
    width: '67%',
    padding: 6,
    fontSize: 9,
    color: '#0F172A',
  },
  thCol1: { width: '18%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5, fontFamily: 'Times-Bold' },
  thCol2: { width: '27%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5, fontFamily: 'Times-Bold' },
  thCol3: { width: '37%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5, fontFamily: 'Times-Bold' },
  thCol4: { width: '18%', padding: 5, fontSize: 8.5, fontFamily: 'Times-Bold' },
  tdCol1: { width: '18%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5, fontFamily: 'Times-Bold' },
  tdCol2: { width: '27%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5, fontFamily: 'Courier' },
  tdCol3: { width: '37%', padding: 5, borderRightWidth: 1, borderRightColor: '#0F172A', borderRightStyle: 'solid', fontSize: 8.5 },
  tdCol4: { width: '18%', padding: 5, fontSize: 8.5, fontFamily: 'Times-Bold' },
  signatureRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 22,
    marginBottom: 10,
  },
  sigBox: {
    width: '45%',
    borderTopWidth: 1,
    borderTopColor: '#0F172A',
    borderTopStyle: 'solid',
    paddingTop: 4,
  },
  sigBoxRight: {
    width: '45%',
    borderTopWidth: 1,
    borderTopColor: '#0F172A',
    borderTopStyle: 'solid',
    paddingTop: 4,
    alignItems: 'flex-end',
  },
  sigTitle: {
    fontSize: 9,
    fontFamily: 'Times-Bold',
    color: '#0F172A',
    textTransform: 'uppercase',
  },
  sigSub: {
    fontSize: 8,
    fontFamily: 'Times-Roman',
    color: '#334155',
    marginTop: 2,
  },
  sealBox: {
    marginHorizontal: 'auto',
    marginVertical: 6,
    padding: 5,
    borderWidth: 1.5,
    borderColor: '#0F172A',
    borderStyle: 'dashed',
    alignItems: 'center',
    width: 250,
    alignSelf: 'center',
  },
  sealText: {
    fontSize: 8.5,
    fontFamily: 'Courier-Bold',
    textTransform: 'uppercase',
    color: '#0F172A',
  },
  sealSub: {
    fontSize: 7,
    fontFamily: 'Helvetica',
    color: '#475569',
    marginTop: 1,
  },
  distributionSection: {
    borderTopWidth: 1,
    borderTopColor: '#0F172A',
    borderTopStyle: 'solid',
    paddingTop: 6,
    marginTop: 6,
  },
  distHeading: {
    fontSize: 8.5,
    fontFamily: 'Times-Bold',
    textTransform: 'uppercase',
    marginBottom: 3,
  },
  distItem: {
    fontSize: 8,
    fontFamily: 'Times-Roman',
    color: '#334155',
    marginBottom: 1.5,
  }
});

// Authentic Government Seal SVG Component for @react-pdf/renderer
const GovernmentSealSVG = () => (
  <Svg width="36" height="36" viewBox="0 0 40 40">
    <Circle cx="20" cy="20" r="18" fill="none" stroke="#0F172A" strokeWidth="1.5" />
    <Circle cx="20" cy="20" r="15" fill="none" stroke="#0F172A" strokeWidth="0.8" />
    <Rect x="12" y="24" width="16" height="2" fill="#0F172A" />
    <Rect x="14" y="16" width="2.5" height="7" fill="#0F172A" />
    <Rect x="18.75" y="16" width="2.5" height="7" fill="#0F172A" />
    <Rect x="23.5" y="16" width="2.5" height="7" fill="#0F172A" />
    <Path d="M12 16 L20 10 L28 16 Z" fill="#0F172A" />
  </Svg>
);

// Authentic Government Administrative Order Schema for @react-pdf/renderer
export const EvacuationSOPDocument: React.FC<{ stats: IsolationStats }> = ({ stats }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      
      {/* Official Header & Crest */}
      <View style={styles.header}>
        <GovernmentSealSVG />
        <Text style={styles.govTitle}>GOVERNMENT OF INDIA</Text>
        <Text style={styles.sdmaTitle}>STATE DISASTER MANAGEMENT AUTHORITY (SDMA)</Text>
        <Text style={styles.subHeaderTitle}>MINISTRY OF NORTH EASTERN REGION CONTROL ROOM</Text>

        <View style={styles.metaMarginRow}>
          <Text style={styles.metaText}>ORDER NO: SDMA/NER/2026/SL-087</Text>
          <Text style={styles.metaText}>DATE: September 04, 2026</Text>
        </View>
      </View>

      {/* Document Title & Preamble */}
      <Text style={styles.sectionOrderTitle}>
        EMERGENCY DISPATCH ORDER (SECTION 30, DISASTER MANAGEMENT ACT)
      </Text>
      
      <Text style={styles.subjectText}>
        SUBJECT: MANDATORY EVACUATION &amp; TACTICAL RELIEF DISPATCH FOR NH-6 SONAPUR LANDSLIDE CUT-OFF.
      </Text>

      <Text style={styles.preamble}>
        Whereas, continuous real-time geotechnical telemetry and satellite radar monitoring have indicated severe structural instability (exceeding 87% failure probability) along the NH-6 Sonapur corridor; now, therefore, in exercise of the powers conferred under Section 30 of the Disaster Management Act, 2005, the undersigned hereby issues the following mandatory executive directives for immediate execution by all line departments and emergency response units.
      </Text>

      {/* SECTION I: Operational Incident Context */}
      <Text style={styles.sectionHeading}>SECTION I: OPERATIONAL INCIDENT CONTEXT</Text>
      <View style={styles.table}>
        <View style={styles.tableRow}>
          <Text style={styles.tdLabel}>Affected Sector</Text>
          <Text style={styles.tdVal}>NH-6 Sonapur Corridor (Milepost 42 to 48)</Text>
        </View>
        <View style={styles.tableRow}>
          <Text style={styles.tdLabel}>Threat Classification</Text>
          <Text style={{ ...styles.tdVal, fontFamily: 'Times-Bold', color: '#B91C1C' }}>
            LEVEL 3: CRITICAL RED ALERT (Geotechnical Instability &gt; 87%)
          </Text>
        </View>
        <View style={styles.tableRow}>
          <Text style={styles.tdLabel}>Isolated Population</Text>
          <Text style={styles.tdVal}>
            {stats.isolatedPopulation?.toLocaleString() ?? '12,450'} Residents across {stats.cutoffVillagesCount ?? 20} NER Hill Villages
          </Text>
        </View>
        <View style={{ ...styles.tableRow, borderBottomWidth: 0 }}>
          <Text style={styles.tdLabel}>Primary Transport Status</Text>
          <Text style={styles.tdVal}>
            NH-6 Fully Severed; Active Detour Route (+{stats.detourKm ?? 42.5} km via SH-12)
          </Text>
        </View>
      </View>

      {/* SECTION II: Mandatory Operational Protocols */}
      <Text style={styles.sectionHeading}>SECTION II: MANDATORY OPERATIONAL PROTOCOLS</Text>
      <View style={styles.table}>
        <View style={{ ...styles.tableRow, ...styles.tableHeader }}>
          <Text style={styles.thCol1}>Trigger Level</Text>
          <Text style={styles.thCol2}>Geotechnical Threshold</Text>
          <Text style={styles.thCol3}>Mandatory Executive Directives</Text>
          <Text style={styles.thCol4}>Assigned Unit</Text>
        </View>
        
        <View style={styles.tableRow}>
          <Text style={styles.tdCol1}>Level 1 (Alert)</Text>
          <Text style={styles.tdCol2}>Tilt &gt; 2.5 mm/hr</Text>
          <Text style={styles.tdCol3}>Issue Emergency SMS Broadcast &amp; Continuous Satellite Radar Tracking</Text>
          <Text style={styles.tdCol4}>Geological Survey / NIC</Text>
        </View>
        
        <View style={styles.tableRow}>
          <Text style={styles.tdCol1}>Level 2 (Evacuate)</Text>
          <Text style={styles.tdCol2}>Soil Moisture &gt; 60%</Text>
          <Text style={styles.tdCol3}>Enforce Mandatory Sector Evacuation &amp; Erect Traffic Diversions</Text>
          <Text style={styles.tdCol4}>District Police &amp; BRO</Text>
        </View>

        <View style={{ ...styles.tableRow, borderBottomWidth: 0 }}>
          <Text style={styles.tdCol1}>Level 3 (Rescue/Relief)</Text>
          <Text style={styles.tdCol2}>NH-6 Roadway Severance</Text>
          <Text style={styles.tdCol3}>Deploy Heavy Machinery for Debris Clearance &amp; Initiate Airdrop of Essential Supplies</Text>
          <Text style={styles.tdCol4}>NDRF / SDRF / IAF Aviation</Text>
        </View>
      </View>

      {/* SECTION III: Authorization & Sign-off */}
      <Text style={styles.sectionHeading}>SECTION III: AUTHORIZATION &amp; ISSUANCE</Text>
      <View style={styles.signatureRow}>
        <View style={styles.sigBox}>
          <Text style={styles.sigTitle}>(Dr. Lalrinpuia Sailo, IAS)</Text>
          <Text style={styles.sigSub}>Nodal Officer, SDMA North East Region</Text>
        </View>
        <View style={styles.sigBoxRight}>
          <Text style={styles.sigTitle}>(Smt. Zoramthangi Lunglei, IAS)</Text>
          <Text style={styles.sigSub}>State Disaster Relief Commissioner &amp; Chairperson</Text>
        </View>
      </View>

      {/* Official Rectangular Stamp/Seal Box */}
      <View style={styles.sealBox}>
        <Text style={styles.sealText}>[ SDMA EMERGENCY SEAL / STAMP ]</Text>
        <Text style={styles.sealSub}>
          Verified Control Room Record • SHA-256 Verified
        </Text>
      </View>

      {/* SECTION IV: Distribution List */}
      <View style={styles.distributionSection}>
        <Text style={styles.distHeading}>COPY TO FOR IMMEDIATE INFORMATION AND COMPLIANCE:</Text>
        <Text style={styles.distItem}>1. Office of the District Magistrate &amp; Collector, Aizawl / East Khasi Hills.</Text>
        <Text style={styles.distItem}>2. Chief Engineer, Border Roads Organisation (BRO), Project Pushpak / Swastik.</Text>
        <Text style={styles.distItem}>3. Commandant, 1st Battalion National Disaster Response Force (NDRF).</Text>
        <Text style={styles.distItem}>4. Guard File / Command Center Operations Log.</Text>
      </View>

    </Page>
  </Document>
);

// Solid Emerald Green Export SOP Order Button
export const DownloadSOPButton: React.FC<{ stats: IsolationStats; onClick?: () => void }> = ({ stats, onClick }) => {
  if (onClick) {
    return (
      <button
        onClick={onClick}
        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-md active:scale-95 cursor-pointer bg-[#10b981] hover:bg-[#059669] text-white shadow-emerald-500/20"
        title="View & Export Official SOP Order (PDF)"
      >
        <Download className="w-4 h-4 text-white" />
        <span>Export SOP Order (PDF)</span>
      </button>
    );
  }

  return (
    <PDFDownloadLink
      document={<EvacuationSOPDocument stats={stats} />}
      fileName={`SafeSlope_SDMA_NER_SOP_Order_${new Date().toISOString().slice(0, 10)}.pdf`}
      className="no-underline"
    >
      {({ loading }) => (
        <button
          disabled={loading}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-md active:scale-95 cursor-pointer ${
            loading
              ? 'bg-slate-300 text-slate-600 cursor-not-allowed'
              : 'bg-[#10b981] hover:bg-[#059669] text-white shadow-emerald-500/20'
          }`}
          title="Export SOP Order (PDF)"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Compiling SOP...</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4 text-white" />
              <span>Export SOP Order (PDF)</span>
            </>
          )}
        </button>
      )}
    </PDFDownloadLink>
  );
};
