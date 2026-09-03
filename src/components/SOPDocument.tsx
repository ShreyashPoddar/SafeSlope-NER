import React from 'react';
import { 
  Document, 
  Page, 
  Text, 
  View, 
  StyleSheet, 
  PDFDownloadLink
} from '@react-pdf/renderer';
import { Download, Loader2 } from 'lucide-react';
import type { IsolationStats } from '../types/dashboard';

// PDF Document Stylesheet
const styles = StyleSheet.create({
  page: {
    padding: 35,
    backgroundColor: '#FFFFFF',
    fontFamily: 'Helvetica',
    fontSize: 10,
    color: '#1E293B',
  },
  headerBanner: {
    backgroundColor: '#0F172A',
    color: '#FFFFFF',
    padding: 15,
    borderRadius: 4,
    marginBottom: 15,
    textAlign: 'center',
  },
  title: {
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 0.5,
    color: '#F8FAFC',
    textTransform: 'uppercase',
  },
  subtitle: {
    fontSize: 10,
    color: '#34D399',
    marginTop: 4,
    fontWeight: 'bold',
  },
  metaGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
    borderBottomStyle: 'solid',
    paddingBottom: 10,
    marginBottom: 15,
  },
  metaItem: {
    flexDirection: 'column',
  },
  metaLabel: {
    fontSize: 8,
    color: '#64748B',
    textTransform: 'uppercase',
    fontWeight: 'bold',
  },
  metaValue: {
    fontSize: 10,
    color: '#0F172A',
    fontWeight: 'bold',
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#047857',
    borderBottomWidth: 1.5,
    borderBottomColor: '#10B981',
    borderBottomStyle: 'solid',
    paddingBottom: 4,
    marginTop: 12,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    padding: 10,
    borderRadius: 4,
    marginBottom: 12,
  },
  summaryCard: {
    flex: 1,
    padding: 6,
  },
  summaryValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#0F172A',
  },
  summaryLabel: {
    fontSize: 8,
    color: '#64748B',
    marginTop: 2,
  },
  table: {
    marginTop: 8,
    marginBottom: 12,
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
    borderBottomStyle: 'solid',
    paddingVertical: 6,
    alignItems: 'center',
  },
  tableHeader: {
    backgroundColor: '#F1F5F9',
    fontWeight: 'bold',
  },
  colLevel: { width: '20%', fontWeight: 'bold', color: '#0F172A' },
  colTrigger: { width: '35%', color: '#334155' },
  colAction: { width: '45%', color: '#0F172A' },
  signatureSection: {
    marginTop: 25,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sigBox: {
    width: '45%',
    borderTopWidth: 1,
    borderTopColor: '#94A3B8',
    borderTopStyle: 'solid',
    paddingTop: 6,
  },
  sigTitle: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#334155',
  },
  sigSub: {
    fontSize: 8,
    color: '#64748B',
    marginTop: 2,
  },
  footer: {
    position: 'absolute',
    bottom: 20,
    left: 35,
    right: 35,
    textAlign: 'center',
    fontSize: 8,
    color: '#94A3B8',
  }
});

// React PDF Evacuation SOP Document Schema for North Eastern Region (NER)
export const EvacuationSOPDocument: React.FC<{ stats: IsolationStats }> = ({ stats }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      
      {/* Official Header */}
      <View style={styles.headerBanner}>
        <Text style={styles.title}>STATE DISASTER MANAGEMENT AUTHORITY (SDMA)</Text>
        <Text style={styles.subtitle}>NORTH EASTERN REGION (NER) // EMERGENCY DISPATCH ORDER</Text>
      </View>

      {/* Metadata Bar */}
      <View style={styles.metaGrid}>
        <View style={styles.metaItem}>
          <Text style={styles.metaLabel}>Order Reference</Text>
          <Text style={styles.metaValue}>SDMA/NER/2026/SL-087</Text>
        </View>
        <View style={styles.metaItem}>
          <Text style={styles.metaLabel}>Dispatch Timestamp</Text>
          <Text style={styles.metaValue}>04-SEP-2026 00:47 IST</Text>
        </View>
        <View style={styles.metaItem}>
          <Text style={styles.metaLabel}>Threat Level</Text>
          <Text style={{ ...styles.metaValue, color: '#DC2626' }}>LEVEL 3: CRITICAL RED ALERT</Text>
        </View>
      </View>

      {/* Incident Context Summary */}
      <Text style={styles.sectionTitle}>1. Incident Context & Telemetry Summary</Text>
      <View style={styles.summaryGrid}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryValue}>{stats.isolatedPopulation?.toLocaleString() ?? '12,450'}</Text>
          <Text style={styles.summaryLabel}>Total Isolated Population</Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryValue}>{stats.cutoffVillagesCount ?? 20} NER Villages</Text>
          <Text style={styles.summaryLabel}>Cut-off Communities</Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryValue}>{stats.primaryCutoffRoad ?? 'NH-6 Sonapur Cut'}</Text>
          <Text style={styles.summaryLabel}>Primary Severed Route</Text>
        </View>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryValue}>+{stats.detourKm ?? 42.5} km</Text>
          <Text style={styles.summaryLabel}>Active Bypass Detour</Text>
        </View>
      </View>

      {/* Operational Response Matrix */}
      <Text style={styles.sectionTitle}>2. Operational Response Protocols</Text>
      <View style={styles.table}>
        <View style={{ ...styles.tableRow, ...styles.tableHeader }}>
          <Text style={styles.colLevel}>Trigger Level</Text>
          <Text style={styles.colTrigger}>Condition</Text>
          <Text style={styles.colAction}>Mandatory Action</Text>
        </View>
        
        <View style={styles.tableRow}>
          <Text style={styles.colLevel}>Level 1: Alert</Text>
          <Text style={styles.colTrigger}>Tilt Acceleration &gt; 2.5 mm/hr</Text>
          <Text style={styles.colAction}>SMS Broadcast &amp; Satellite Radar Tracking</Text>
        </View>
        
        <View style={styles.tableRow}>
          <Text style={styles.colLevel}>Level 2: Evacuate</Text>
          <Text style={styles.colTrigger}>Soil Moisture Saturation &gt; 60%</Text>
          <Text style={styles.colAction}>Mandatory Sector Evacuation &amp; Detour Signs</Text>
        </View>

        <View style={styles.tableRow}>
          <Text style={styles.colLevel}>Level 3: Rescue</Text>
          <Text style={styles.colTrigger}>NH-6 Sonapur Severance</Text>
          <Text style={styles.colAction}>Airdrop Medical Supplies &amp; BRO Excavators</Text>
        </View>
      </View>

      {/* Signatures */}
      <View style={styles.signatureSection}>
        <View style={styles.sigBox}>
          <Text style={styles.sigTitle}>Dr. Lalrinpuia Sailo, IAS</Text>
          <Text style={styles.sigSub}>Nodal Officer, SDMA North East</Text>
        </View>
        <View style={styles.sigBox}>
          <Text style={styles.sigTitle}>Smt. Zoramthangi Lunglei, IAS</Text>
          <Text style={styles.sigSub}>State Disaster Relief Commissioner, SDMA</Text>
        </View>
      </View>

      <Text style={styles.footer}>
        CONFIDENTIAL - FOR OFFICIAL SAFESLOPE COMMAND CENTER DISPATCH USE ONLY
      </Text>
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
