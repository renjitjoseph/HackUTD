import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { getRandomCustomer } from './customerData';
import { createClient } from '@supabase/supabase-js';
import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Supabase config
const SUPABASE_URL = 'https://xmyjprtuztwqqovonrzb.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhteWpwcnR1enR3cXFvdm9ucnpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2NTY2NTQsImV4cCI6MjA3ODIzMjY1NH0.sC1hue1SeB5iJJypKKkVHcQ5Gup7ckKX-yP79tUN9Ek';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});

export default function CustomerProfile({ navigation, route }) {
  const [customerData, setCustomerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentInsight, setCurrentInsight] = useState(null);

  // Get customer ID from route params (if passed from active session)
  const customerId = route?.params?.customerId;

  // Collapsible section states - first two start collapsed
  const [accountExpanded, setAccountExpanded] = useState(false);
  const [planExpanded, setPlanExpanded] = useState(false);
  const [personalExpanded, setPersonalExpanded] = useState(true);
  const [professionalExpanded, setProfessionalExpanded] = useState(true);
  const [salesExpanded, setSalesExpanded] = useState(true);

  useEffect(() => {
    // Fetch customer from Supabase
    const fetchCustomer = async () => {
      setLoading(true);

      if (customerId) {
        // Fetch specific customer by ID
        const { getCustomerById } = require('./customerData');
        const customer = await getCustomerById(customerId);
        setCustomerData(customer || await getRandomCustomer());
      } else {
        // Fetch random customer
        const randomCustomer = await getRandomCustomer();
        setCustomerData(randomCustomer);
      }

      setLoading(false);
    };

    fetchCustomer();
  }, [customerId]);

  // Poll for AI insights every 2 seconds
  useEffect(() => {
    const pollInsights = async () => {
      try {
        const { data, error } = await supabase
          .from('active_session')
          .select('current_insight')
          .eq('id', 1)
          .single();

        if (!error && data && data.current_insight) {
          setCurrentInsight(data.current_insight);
        }
      } catch (error) {
        console.error('Error polling insights:', error);
      }
    };

    // Run immediately
    pollInsights();

    // Poll every 2 seconds
    const pollInterval = setInterval(pollInsights, 2000);

    // Cleanup
    return () => clearInterval(pollInterval);
  }, []);

  if (loading || !customerData) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />
        <LinearGradient
          colors={['#E20074', '#D4006E']}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <TouchableOpacity 
              style={styles.backButton}
              onPress={() => navigation.goBack()}
            >
              <Ionicons name="arrow-back" size={24} color="#FFF" />
            </TouchableOpacity>
            <Text style={styles.headerTitle}>Customer Profile</Text>
            <View style={{ width: 40 }} />
          </View>
        </LinearGradient>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#E20074" />
          <Text style={styles.loadingText}>Loading customer data...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      {/* Header */}
      <LinearGradient
        colors={['#E20074', '#D4006E']}
        style={styles.header}
      >
        <View style={styles.headerContent}>
          <TouchableOpacity 
            style={styles.backButton}
            onPress={() => navigation.goBack()}
          >
            <Ionicons name="arrow-back" size={24} color="#FFF" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Customer Profile</Text>
          <View style={{ width: 40 }} />
        </View>
      </LinearGradient>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Customer Avatar and Name */}
        <View style={styles.profileHeader}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person" size={50} color="#E20074" />
          </View>
          <Text style={styles.customerName}>{customerData.name}</Text>
          <View style={styles.statusBadge}>
            <Text style={styles.statusText}>{customerData.status}</Text>
          </View>
          <Text style={styles.customerId}>ID: {customerData.id}</Text>
        </View>

        {/* AI Insight Card - Right below name section */}
        {currentInsight && (
          <View style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <Ionicons name="bulb" size={22} color="#E20074" />
              <Text style={styles.insightTitle}>AI Recommendation</Text>
            </View>

            <View style={styles.insightContent}>
              <View style={styles.insightStatusRow}>
                <Text style={styles.insightStatusText}>{currentInsight.status}</Text>
                {currentInsight.score && (
                  <View style={styles.insightScoreBadge}>
                    <Text style={styles.insightScoreText}>{currentInsight.score}/10</Text>
                  </View>
                )}
              </View>

              {currentInsight.reason && (
                <Text style={styles.insightReason}>{currentInsight.reason}</Text>
              )}

              {currentInsight.recommendation && (
                <View style={styles.recommendationBox}>
                  <Text style={styles.recommendationLabel}>Say this:</Text>
                  <Text style={styles.recommendationText}>"{currentInsight.recommendation}"</Text>
                </View>
              )}
            </View>
          </View>
        )}

        {/* Compact Info Grid - Collapsible */}
        <View style={styles.compactCard}>
          <TouchableOpacity
            style={styles.collapsibleHeader}
            onPress={() => setAccountExpanded(!accountExpanded)}
            activeOpacity={0.7}
          >
            <Text style={styles.collapsibleTitle}>Account Info</Text>
            <Ionicons
              name={accountExpanded ? "chevron-up" : "chevron-down"}
              size={24}
              color="#E20074"
            />
          </TouchableOpacity>

          {accountExpanded && (
            <>
              <View style={styles.gridRow}>
                <View style={styles.gridItem}>
                  <Ionicons name="card-outline" size={18} color="#E20074" />
                  <Text style={styles.gridLabel}>Account</Text>
                  <Text style={styles.gridValue}>{customerData.accountNumber}</Text>
                </View>
                <View style={styles.gridItem}>
                  <Ionicons name="call-outline" size={18} color="#E20074" />
                  <Text style={styles.gridLabel}>Phone</Text>
                  <Text style={styles.gridValue}>{customerData.phoneNumber}</Text>
                </View>
              </View>

              <View style={styles.gridRow}>
                <View style={styles.gridItem}>
                  <Ionicons name="time-outline" size={18} color="#E20074" />
                  <Text style={styles.gridLabel}>Member</Text>
                  <Text style={styles.gridValue}>{customerData.accountAge}</Text>
                </View>
                <View style={styles.gridItem}>
                  <Ionicons name="phone-portrait-outline" size={18} color="#E20074" />
                  <Text style={styles.gridLabel}>Device</Text>
                  <Text style={styles.gridValue}>{customerData.deviceModel}</Text>
                </View>
              </View>
            </>
          )}
        </View>

        {/* Plan & Billing Compact - Collapsible */}
        <View style={styles.compactCard}>
          <TouchableOpacity
            style={styles.collapsibleHeader}
            onPress={() => setPlanExpanded(!planExpanded)}
            activeOpacity={0.7}
          >
            <View style={styles.planHeaderCollapsed}>
              <Text style={styles.collapsibleTitle}>Plan & Billing</Text>
              <Text style={styles.planPreview}>{customerData.plan} • {customerData.monthlyBill}/mo</Text>
            </View>
            <Ionicons
              name={planExpanded ? "chevron-up" : "chevron-down"}
              size={24}
              color="#E20074"
            />
          </TouchableOpacity>

          {planExpanded && (
            <>
              <View style={styles.planHeader}>
                <Text style={styles.planBadgeText}>{customerData.plan}</Text>
                <Text style={styles.billAmount}>{customerData.monthlyBill}/mo</Text>
              </View>

              <View style={styles.gridRow}>
                <View style={styles.gridItem}>
                  <Ionicons name="cellular-outline" size={18} color="#E20074" />
                  <Text style={styles.gridLabel}>Data Used</Text>
                  <Text style={styles.gridValue}>{customerData.dataUsage}</Text>
                </View>
                <View style={styles.gridItem}>
                  <Ionicons name="star" size={18} color="#FFD700" />
                  <Text style={styles.gridLabel}>Points</Text>
                  <Text style={styles.gridValue}>{customerData.loyaltyPoints.toLocaleString()}</Text>
                </View>
              </View>

              <View style={styles.gridRow}>
                <View style={styles.gridItem}>
                  <Ionicons name="checkmark-circle-outline" size={18} color="#4CAF50" />
                  <Text style={styles.gridLabel}>Last Payment</Text>
                  <Text style={styles.gridValue}>{customerData.lastPayment}</Text>
                </View>
                <View style={styles.gridItem}>
                  <Ionicons name="calendar-outline" size={18} color="#666" />
                  <Text style={styles.gridLabel}>Next Bill</Text>
                  <Text style={styles.gridValue}>{customerData.nextBillDate}</Text>
                </View>
              </View>
            </>
          )}
        </View>

        {/* Personal Details Section - Collapsible */}
        {customerData.personalDetails && customerData.personalDetails.length > 0 && (
          <View style={styles.compactCard}>
            <TouchableOpacity
              style={styles.collapsibleHeader}
              onPress={() => setPersonalExpanded(!personalExpanded)}
              activeOpacity={0.7}
            >
              <View style={styles.sectionHeaderCollapsed}>
                <Ionicons name="home" size={20} color="#E20074" />
                <Text style={styles.collapsibleTitle}>Personal Details</Text>
              </View>
              <Ionicons
                name={personalExpanded ? "chevron-up" : "chevron-down"}
                size={24}
                color="#E20074"
              />
            </TouchableOpacity>

            {personalExpanded && (
              <View style={styles.expandedContent}>
                {customerData.personalDetails.map((detail, index) => (
                  <View key={index} style={styles.bulletItem}>
                    <Text style={styles.bulletDot}>•</Text>
                    <Text style={styles.bulletText}>{detail}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* Professional Details Section - Collapsible */}
        {customerData.professionalDetails && customerData.professionalDetails.length > 0 && (
          <View style={styles.compactCard}>
            <TouchableOpacity
              style={styles.collapsibleHeader}
              onPress={() => setProfessionalExpanded(!professionalExpanded)}
              activeOpacity={0.7}
            >
              <View style={styles.sectionHeaderCollapsed}>
                <Ionicons name="briefcase" size={20} color="#E20074" />
                <Text style={styles.collapsibleTitle}>Professional Details</Text>
              </View>
              <Ionicons
                name={professionalExpanded ? "chevron-up" : "chevron-down"}
                size={24}
                color="#E20074"
              />
            </TouchableOpacity>

            {professionalExpanded && (
              <View style={styles.expandedContent}>
                {customerData.professionalDetails.map((detail, index) => (
                  <View key={index} style={styles.bulletItem}>
                    <Text style={styles.bulletDot}>•</Text>
                    <Text style={styles.bulletText}>{detail}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* Sales Context Section - Collapsible */}
        {customerData.salesContext && customerData.salesContext.length > 0 && (
          <View style={styles.compactCard}>
            <TouchableOpacity
              style={styles.collapsibleHeader}
              onPress={() => setSalesExpanded(!salesExpanded)}
              activeOpacity={0.7}
            >
              <View style={styles.sectionHeaderCollapsed}>
                <Ionicons name="cart" size={20} color="#E20074" />
                <Text style={styles.collapsibleTitle}>Sales Context</Text>
              </View>
              <Ionicons
                name={salesExpanded ? "chevron-up" : "chevron-down"}
                size={24}
                color="#E20074"
              />
            </TouchableOpacity>

            {salesExpanded && (
              <View style={styles.expandedContent}>
                {customerData.salesContext.map((detail, index) => (
                  <View key={index} style={styles.bulletItem}>
                    <Text style={styles.bulletDot}>•</Text>
                    <Text style={styles.bulletText}>{detail}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="chatbubble-outline" size={22} color="#E20074" />
            <Text style={styles.actionButtonText}>Message</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="call-outline" size={22} color="#E20074" />
            <Text style={styles.actionButtonText}>Call</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="mail-outline" size={22} color="#E20074" />
            <Text style={styles.actionButtonText}>Email</Text>
          </TouchableOpacity>
        </View>

        {/* Extra spacing */}
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    paddingTop: 10,
    paddingBottom: 20,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFF',
  },
  scrollView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    color: '#666',
  },
  profileHeader: {
    alignItems: 'center',
    paddingVertical: 25,
    backgroundColor: '#FFF',
    borderBottomLeftRadius: 25,
    borderBottomRightRadius: 25,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  avatarContainer: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: '#FFE6F5',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 3,
    borderColor: '#E20074',
  },
  customerName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  statusBadge: {
    backgroundColor: '#E20074',
    paddingHorizontal: 16,
    paddingVertical: 5,
    borderRadius: 15,
    marginBottom: 5,
  },
  statusText: {
    color: '#FFF',
    fontWeight: '600',
    fontSize: 13,
  },
  customerId: {
    fontSize: 13,
    color: '#999',
    marginTop: 5,
  },
  compactCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 15,
    marginBottom: 15,
    padding: 18,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  gridRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 18,
  },
  gridItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  gridLabel: {
    fontSize: 11,
    color: '#999',
    marginTop: 5,
    marginBottom: 3,
  },
  gridValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#000',
    textAlign: 'center',
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFE6F5',
    padding: 12,
    borderRadius: 10,
    marginBottom: 18,
    borderWidth: 2,
    borderColor: '#E20074',
  },
  planBadgeText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E20074',
  },
  billAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#E20074',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginHorizontal: 15,
    marginTop: 5,
  },
  actionButton: {
    backgroundColor: '#FFF',
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
    flex: 1,
    marginHorizontal: 5,
  },
  actionButtonText: {
    color: '#E20074',
    fontWeight: '600',
    marginTop: 6,
    fontSize: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    marginLeft: 10,
  },
  bulletItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  bulletDot: {
    fontSize: 16,
    color: '#E20074',
    marginRight: 10,
    marginTop: 2,
  },
  bulletText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    lineHeight: 20,
  },
  collapsibleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 5,
  },
  collapsibleTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
  },
  sectionHeaderCollapsed: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  planHeaderCollapsed: {
    flex: 1,
  },
  planPreview: {
    fontSize: 13,
    color: '#666',
    marginTop: 3,
  },
  expandedContent: {
    marginTop: 15,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#F0F0F0',
  },
  insightCard: {
    backgroundColor: '#FFF',
    marginHorizontal: 15,
    marginBottom: 15,
    padding: 18,
    borderRadius: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#E20074',
    shadowColor: '#E20074',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 5,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E20074',
    marginLeft: 8,
  },
  insightContent: {
    gap: 10,
  },
  insightStatusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
  },
  insightStatusText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  insightScoreBadge: {
    backgroundColor: '#E20074',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 10,
  },
  insightScoreText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 13,
  },
  insightReason: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    fontStyle: 'italic',
  },
  recommendationBox: {
    backgroundColor: '#FFF5FA',
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFD4E8',
  },
  recommendationLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#E20074',
    marginBottom: 5,
    textTransform: 'uppercase',
  },
  recommendationText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
    fontWeight: '500',
  },
});

