import React from 'react';
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

export default function App() {
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
        {/* Magenta Status Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Magenta Status</Text>
          <Text style={styles.cardSubtitle}>
            Premium benefits. Brands you love. Get your VIP vibes.
          </Text>
          
          {/* Magenta Status Banner */}
          <LinearGradient
            colors={['#E20074', '#D4006E']}
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

        {/* Extra spacing for bottom nav */}
        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity style={styles.navItem}>
          <MaterialCommunityIcons name="ticket-percent-outline" size={24} color="#666" />
          <Text style={styles.navLabel}>Status</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.navItem}>
          <Ionicons name="location-outline" size={24} color="#666" />
          <Text style={styles.navLabel}>Connect</Text>
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
    color: '#E20074',
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
    backgroundColor: '#E20074',
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
    backgroundColor: '#E20074',
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
    color: '#E20074',
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
});

