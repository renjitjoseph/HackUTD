import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  StatusBar,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
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

export default function ConnectScreen({ navigation }) {
  const [sessionActive, setSessionActive] = useState(false);
  const [currentCustomerId, setCurrentCustomerId] = useState(null);
  const [currentInsight, setCurrentInsight] = useState(null);

  useEffect(() => {
    // Function to poll active session
    const pollActiveSession = async () => {
      try {
        const { data, error } = await supabase
          .from('active_session')
          .select('*')
          .eq('id', 1)
          .single();

        if (!error && data) {
          console.log('📊 Active Session:', {
            status: data.status,
            customer_id: data.current_customer_id,
            confidence: data.confidence_level,
            insight: data.current_insight
          });
          setSessionActive(data.status === 'active');
          setCurrentCustomerId(data.current_customer_id);
          setCurrentInsight(data.current_insight);
        } else if (error) {
          console.error('Error polling active session:', error);
        }
      } catch (error) {
        console.error('Error polling active session:', error);
      }
    };

    // Run immediately on mount
    pollActiveSession();

    // Poll active_session every 2 seconds
    const pollInterval = setInterval(pollActiveSession, 2000);

    // Cleanup on unmount
    return () => clearInterval(pollInterval);
  }, []);

  const handleFABPress = () => {
    if (currentCustomerId) {
      // Navigate with the current customer ID
      navigation.navigate('CustomerProfile', { customerId: currentCustomerId });
    } else {
      console.log('No customer detected yet');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.bankName}>PNC</Text>
          <Text style={styles.greeting}>Welcome back, Anne</Text>
        </View>
        <View style={styles.headerIcons}>
          <TouchableOpacity style={styles.iconButton}>
            <Ionicons name="search-outline" size={24} color="#000" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton}>
            <Ionicons name="notifications-outline" size={24} color="#000" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* AI Insight Card - Only visible when insight is available */}
        {currentInsight && (
          <View style={styles.insightCard}>
            <View style={styles.insightHeader}>
               <Ionicons name="bulb" size={24} color="#FF8C00" />
              <Text style={styles.insightTitle}>AI Recommendation</Text>
            </View>

            <View style={styles.insightContent}>
              <View style={styles.statusBadge}>
                <Text style={styles.statusBadgeText}>{currentInsight.status}</Text>
                {currentInsight.score && (
                  <View style={styles.scoreBadge}>
                    <Text style={styles.scoreText}>{currentInsight.score}/10</Text>
                  </View>
                )}
              </View>

              {currentInsight.reason && (
                <Text style={styles.reasonText}>{currentInsight.reason}</Text>
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

        {/* Account Summary Card */}
        <View style={styles.card}>
          <View style={styles.accountHeader}>
            <Text style={styles.cardTitle}>Total Balance</Text>
            <Ionicons name="eye-outline" size={20} color="#666" />
          </View>
          
          {/* Balance Display */}
          <View style={styles.balanceContainer}>
            <Text style={styles.balanceAmount}>$12,847.52</Text>
            <View style={styles.balanceChange}>
              <Ionicons name="trending-up" size={16} color="#4CAF50" />
              <Text style={styles.balanceChangeText}>+2.3% this month</Text>
            </View>
          </View>

          {/* Account Cards */}
          <View style={styles.accountCards}>
            <LinearGradient
              colors={['#FF8C00', '#FF6B00']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.accountCard}
            >
              <Text style={styles.accountType}>Checking</Text>
              <Text style={styles.accountNumber}>••••5429</Text>
              <Text style={styles.accountBalance}>$8,547.32</Text>
            </LinearGradient>

            <LinearGradient
              colors={['#2C2C2C', '#1A1A1A']}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 1 }}
              style={styles.accountCard}
            >
              <Text style={styles.accountType}>Savings</Text>
              <Text style={styles.accountNumber}>••••8291</Text>
              <Text style={styles.accountBalance}>$4,300.20</Text>
            </LinearGradient>
          </View>
        </View>

        {/* Quick Actions section */}
        <View style={styles.offersSection}>
          <View style={styles.offerHeader}>
            <View>
              <Text style={styles.myStuffLabel}>Quick Actions</Text>
              <Text style={styles.offersTitle}>What would you like to do?</Text>
            </View>
          </View>

          <View style={styles.quickActionsGrid}>
            {/* Transfer Money */}
            <TouchableOpacity style={styles.quickActionCard}>
              <View style={styles.quickActionIcon}>
                <Ionicons name="swap-horizontal" size={28} color="#FF8C00" />
              </View>
              <Text style={styles.quickActionText}>Transfer</Text>
            </TouchableOpacity>

            {/* Pay Bills */}
            <TouchableOpacity style={styles.quickActionCard}>
              <View style={styles.quickActionIcon}>
                <Ionicons name="document-text" size={28} color="#FF8C00" />
              </View>
              <Text style={styles.quickActionText}>Pay Bills</Text>
            </TouchableOpacity>

            {/* Deposit Check */}
            <TouchableOpacity style={styles.quickActionCard}>
              <View style={styles.quickActionIcon}>
                <Ionicons name="camera" size={28} color="#FF8C00" />
              </View>
              <Text style={styles.quickActionText}>Deposit</Text>
            </TouchableOpacity>

            {/* Send Money */}
            <TouchableOpacity style={styles.quickActionCard}>
              <View style={styles.quickActionIcon}>
                <Ionicons name="paper-plane" size={28} color="#FF8C00" />
              </View>
              <Text style={styles.quickActionText}>Send</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Recent Transactions */}
        <View style={styles.transactionsSection}>
          <View style={styles.offerHeader}>
            <Text style={styles.offersTitle}>Recent Transactions</Text>
            <TouchableOpacity>
              <Text style={styles.viewAllText}>View All</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.transactionsList}>
            <View style={styles.transactionItem}>
              <View style={styles.transactionIcon}>
                <Ionicons name="cafe" size={24} color="#FF8C00" />
              </View>
              <View style={styles.transactionDetails}>
                <Text style={styles.transactionName}>Starbucks Coffee</Text>
                <Text style={styles.transactionDate}>Today, 9:45 AM</Text>
              </View>
              <Text style={styles.transactionAmount}>-$5.67</Text>
            </View>

            <View style={styles.transactionItem}>
              <View style={styles.transactionIcon}>
                <Ionicons name="cart" size={24} color="#FF8C00" />
              </View>
              <View style={styles.transactionDetails}>
                <Text style={styles.transactionName}>Amazon Purchase</Text>
                <Text style={styles.transactionDate}>Yesterday</Text>
              </View>
              <Text style={styles.transactionAmount}>-$89.99</Text>
            </View>

            <View style={styles.transactionItem}>
              <View style={styles.transactionIcon}>
                <Ionicons name="arrow-down" size={24} color="#4CAF50" />
              </View>
              <View style={styles.transactionDetails}>
                <Text style={styles.transactionName}>Paycheck Deposit</Text>
                <Text style={styles.transactionDate}>Nov 7</Text>
              </View>
              <Text style={[styles.transactionAmount, { color: '#4CAF50' }]}>+$2,450.00</Text>
            </View>
          </View>
        </View>

        {/* Extra spacing for bottom nav and FAB */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity 
          style={styles.navItem}
          onPress={() => navigation.navigate('Home')}
        >
          <MaterialCommunityIcons name="ticket-percent-outline" size={24} color="#666" />
          <Text style={styles.navLabel}>Status</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.navItem}
          onPress={() => navigation.navigate('Connect')}
        >
          <Ionicons name="location" size={24} color="#FF8C00" />
          <Text style={[styles.navLabel, { color: '#FF8C00' }]}>Connect</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="bag-outline" size={24} color="#666" />
          <Text style={styles.navLabel}>Shop</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="person-outline" size={24} color="#666" />
          <Text style={styles.navLabel}>Manage</Text>
        </TouchableOpacity>
      </View>

      {/* Floating Action Button - Only visible when session is active */}
      {sessionActive && (
        <TouchableOpacity
          style={[styles.fab, !currentCustomerId && styles.fabDetecting]}
          onPress={handleFABPress}
          activeOpacity={0.8}
        >
          {currentCustomerId ? (
            <Ionicons name="person" size={28} color="#FFF" />
          ) : (
            <Ionicons name="scan" size={28} color="#FFF" />
          )}
        </TouchableOpacity>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#FFF',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  headerLeft: {
    flex: 1,
  },
  bankName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FF8C00',
    letterSpacing: 1,
  },
  greeting: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  headerIcons: {
    flexDirection: 'row',
    gap: 15,
  },
  iconButton: {
    padding: 5,
  },
  scrollView: {
    flex: 1,
  },
  insightCard: {
    backgroundColor: '#FFF',
    margin: 15,
    marginTop: 15,
    padding: 20,
    borderRadius: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#FF8C00',
    shadowColor: '#FF8C00',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 5,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  insightTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FF8C00',
    marginLeft: 10,
  },
  insightContent: {
    gap: 12,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F5F5F5',
    padding: 12,
    borderRadius: 8,
  },
  statusBadgeText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  scoreBadge: {
    backgroundColor: '#FF8C00',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
  },
  scoreText: {
    color: '#FFF',
    fontWeight: 'bold',
    fontSize: 14,
  },
  reasonText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    fontStyle: 'italic',
  },
  recommendationBox: {
    backgroundColor: '#FFF5FA',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FFD4E8',
  },
  recommendationLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FF8C00',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  recommendationText: {
    fontSize: 15,
    color: '#333',
    lineHeight: 22,
    fontWeight: '500',
  },
  card: {
    backgroundColor: '#FFF',
    margin: 15,
    marginTop: 20,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    lineHeight: 20,
  },
  accountHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  balanceContainer: {
    marginBottom: 20,
  },
  balanceAmount: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 8,
  },
  balanceChange: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  balanceChangeText: {
    fontSize: 14,
    color: '#4CAF50',
    fontWeight: '500',
  },
  accountCards: {
    flexDirection: 'row',
    gap: 15,
  },
  accountCard: {
    flex: 1,
    padding: 20,
    borderRadius: 12,
    height: 140,
    justifyContent: 'space-between',
  },
  accountType: {
    fontSize: 14,
    color: '#FFF',
    opacity: 0.9,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  accountNumber: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: '500',
  },
  accountBalance: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFF',
  },
  offersSection: {
    backgroundColor: '#FFF',
    margin: 15,
    marginTop: 5,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  offerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  myStuffLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  offersTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 15,
  },
  quickActionCard: {
    width: '47%',
    backgroundColor: '#FFF',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#F0F0F0',
  },
  quickActionIcon: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FFF5E6',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  quickActionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  transactionsSection: {
    backgroundColor: '#FFF',
    margin: 15,
    marginTop: 5,
    padding: 20,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  transactionsList: {
    gap: 15,
  },
  transactionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F5F5F5',
  },
  transactionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#FFF5E6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  transactionDetails: {
    flex: 1,
  },
  transactionName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#000',
    marginBottom: 4,
  },
  transactionDate: {
    fontSize: 13,
    color: '#999',
  },
  transactionAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
  },
  viewAllText: {
    fontSize: 14,
    color: '#FF8C00',
    fontWeight: '600',
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    paddingVertical: 10,
    paddingBottom: 5,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    justifyContent: 'space-around',
  },
  navItem: {
    alignItems: 'center',
    paddingVertical: 5,
  },
  navLabel: {
    fontSize: 11,
    color: '#666',
    marginTop: 4,
  },
  fab: {
    position: 'absolute',
    right: 20,
    bottom: 105,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#FF8C00',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  fabDetecting: {
    backgroundColor: '#FFA500',
    opacity: 0.8,
  },
});

