#!/usr/bin/env python3
"""
Test script to verify email sending fixes
Tests the improved error handling and retry logic
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_smtp_status():
    """Test /api/email/status endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Vérifier le statut SMTP")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/email/status", timeout=10)
        result = response.json()
        
        print(f"✓ Endpoint répondant: {response.status_code}")
        print(f"  - SMTP Configuré: {result.get('smtp_configured')}")
        print(f"  - SMTP Connecté: {result.get('smtp_connected')}")
        print(f"  - Destinataires: {result.get('recipients_count')}")
        print(f"  - Scheduler actif: {result.get('scheduler_running')}")
        
        return result.get('smtp_connected', False)
    except Exception as e:
        print(f"✗ Erreur accès statut: {e}")
        return False

def test_send_test_email():
    """Test /api/email/send-test endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Envoyer un email de test")
    print("="*60)
    
    try:
        payload = {
            "recipient": "ainaerickandrianavalona@gmail.com"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/email/send-test",
            json=payload,
            timeout=60
        )
        result = response.json()
        
        print(f"✓ Endpoint répondant: {response.status_code}")
        print(f"  - Succès: {result.get('success')}")
        print(f"  - Message: {result.get('message', result.get('error', 'N/A'))}")
        
        return result.get('success', False)
    except Exception as e:
        print(f"✗ Erreur envoi test: {e}")
        return False

def test_send_daily_report():
    """Test /api/email/send-report endpoint with improved error handling"""
    print("\n" + "="*60)
    print("TEST 3: Envoyer un rapport quotidien")
    print("="*60)
    
    try:
        payload = {
            "type": "daily"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/email/send-report",
            json=payload,
            timeout=60
        )
        result = response.json()
        
        print(f"✓ Endpoint répondant: {response.status_code}")
        print(f"  - Succès: {result.get('success')}")
        print(f"  - Message: {result.get('message', result.get('error', 'N/A'))}")
        
        # Cette fois, on attend la vraie valeur (pas false positive!)
        return result.get('success', False)
    except Exception as e:
        print(f"✗ Erreur envoi rapport: {e}")
        return False

def main():
    print("\n" + "█"*60)
    print("TESTE LES CORRECTIONS D'ENVOI D'EMAIL")
    print("█"*60)
    
    # Test 1: Status SMTP
    smtp_ok = test_smtp_status()
    
    # Petit délai
    time.sleep(2)
    
    # Test 2: Email de test
    test_ok = test_send_test_email()
    
    # Petit délai
    time.sleep(2)
    
    # Test 3: Rapport quotidien
    report_ok = test_send_daily_report()
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"✓ SMTP Status Test: {'PASS' if smtp_ok else 'FAIL'}")
    print(f"✓ Test Email: {'PASS' if test_ok else 'FAIL'}")
    print(f"✓ Daily Report: {'PASS' if report_ok else 'FAIL'}")
    print("\nREMARQUE: Les changements incluent:")
    print("  1. Retry automatique en cas d'erreur DNS (jusqu'à 3 fois)")
    print("  2. Timeout augmenté pour SMTP (10s au lieu de 5s)")
    print("  3. Reporting du succès basé sur TOUS les envois réussis")
    print("  4. Meilleure gestion des erreurs réseau/DNS")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
