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
        <Text style={styles.greeting}>Hey, Anne</Text>
        <View style={styles.headerIcons}>
          <TouchableOpacity style={styles.iconButton}>
            <Ionicons name="chatbox-outline" size={24} color="#000" />
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

        {/* Magenta Status Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Magenta Status</Text>
          <Text style={styles.cardSubtitle}>
            Premium benefits. Brands you love. Get your VIP vibes.
          </Text>
          
          {/* Magenta Status Banner */}
          <LinearGradient
            colors={['#FF8C00', '#FF6B00']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.magentaBanner}
          >
            <View style={styles.bannerContent}>
              <Text style={styles.tmobileText}>T-MOBILE</Text>
              <Text style={styles.magentaText}>MAGENTA</Text>
              <Text style={styles.statusText}>STATUS</Text>
            </View>
            {/* Decorative circles */}
            <View style={styles.circle1} />
            <View style={styles.circle2} />
            <View style={styles.circle3} />
          </LinearGradient>

          {/* Check it out button */}
          <TouchableOpacity style={styles.checkButton}>
            <Text style={styles.checkButtonText}>Check it out</Text>
          </TouchableOpacity>
        </View>

        {/* Redeem your offers section */}
        <View style={styles.offersSection}>
          <View style={styles.offerHeader}>
            <View>
              <Text style={styles.myStuffLabel}>My Stuff</Text>
              <Text style={styles.offersTitle}>Redeem your offers</Text>
            </View>
            <Ionicons name="chevron-forward" size={24} color="#000" />
          </View>

          <View style={styles.offerCards}>
            {/* T-Mobile Offer Card */}
            <View style={styles.offerCard}>
              <View style={styles.tMobileCard}>
                <Text style={styles.tLogo}>T</Text>
              </View>
            </View>

            {/* Add Offer Card */}
            <View style={styles.offerCard}>
              <View style={styles.addCard}>
                <Text style={styles.plusIcon}>+</Text>
              </View>
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
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FF8C00',
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
  magentaBanner: {
    height: 160,
    borderRadius: 12,
    overflow: 'hidden',
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'flex-start',
    paddingLeft: 20,
    marginBottom: 15,
  },
  bannerContent: {
    zIndex: 2,
  },
  tmobileText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFF',
    letterSpacing: 1,
    marginBottom: 5,
  },
  magentaText: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#FFF',
    letterSpacing: 2,
  },
  statusText: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#FFF',
    letterSpacing: 2,
    textShadowColor: 'rgba(0, 0, 0, 0.1)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
  },
  circle1: {
    position: 'absolute',
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    top: -30,
    right: -20,
  },
  circle2: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    bottom: -20,
    right: 60,
  },
  circle3: {
    position: 'absolute',
    width: 150,
    height: 150,
    borderRadius: 75,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    bottom: -50,
    left: -40,
  },
  checkButton: {
    backgroundColor: '#FF8C00',
    paddingVertical: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  checkButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: '600',
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
  offerCards: {
    flexDirection: 'row',
    gap: 15,
  },
  offerCard: {
    flex: 1,
  },
  tMobileCard: {
    backgroundColor: '#FF8C00',
    borderRadius: 12,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
  },
  tLogo: {
    fontSize: 60,
    fontWeight: 'bold',
    color: '#FFF',
  },
  addCard: {
    backgroundColor: '#FFF',
    borderRadius: 12,
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E0E0E0',
    borderStyle: 'dashed',
  },
  plusIcon: {
    fontSize: 48,
    color: '#FF8C00',
    fontWeight: '300',
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

