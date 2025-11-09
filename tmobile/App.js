import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from './HomeScreen';
import ConnectScreen from './ConnectScreen';
import CustomerProfile from './CustomerProfile';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="Connect" component={ConnectScreen} />
        <Stack.Screen name="CustomerProfile" component={CustomerProfile} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

