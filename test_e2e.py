#!/usr/bin/env python3
"""
Teste E2E da API Assinafy

Autenticação e testes de ponta a ponta nos principais endpoints.
"""
import os
import requests
from dotenv import load_dotenv

# Carregar credenciais
load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

class AssinafyE2ETest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "X-Api-Key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.results = []

    def log(self, test_name, passed, details=""):
        """Registrar resultado do teste"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"   {details}")

    def test_authenticate(self):
        """Test 1: Autenticação com API Key"""
        try:
            response = self.session.get(f"{BASE_URL}/accounts", timeout=10)
            if response.status_code == 200:
                self.log("Autenticação com API Key", True, f"Status: {response.status_code}")
                return True
            else:
                self.log("Autenticação com API Key", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Autenticação com API Key", False, f"Erro: {str(e)}")
            return False

    def test_list_accounts(self):
        """Test 2: Listar contas"""
        try:
            response = self.session.get(f"{BASE_URL}/accounts", timeout=10)
            data = response.json()

            if response.status_code == 200 and "data" in data:
                accounts = data.get("data", [])
                self.log("Listar contas", True, f"Encontradas: {len(accounts)} contas")
                return accounts
            else:
                self.log("Listar contas", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log("Listar contas", False, f"Erro: {str(e)}")
            return []

    def test_list_documents(self, account_id):
        """Test 3: Listar documentos com paginação"""
        try:
            params = {
                "page": 1,
                "per-page": 10,
                "search": ""
            }
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params=params,
                timeout=10
            )
            data = response.json()

            if response.status_code == 200:
                docs = data.get("data", [])
                total = data.get("total", len(docs))
                self.log("Listar documentos", True, f"Docs: {len(docs)}, Total: {total}")
                return docs
            else:
                self.log("Listar documentos", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log("Listar documentos", False, f"Erro: {str(e)}")
            return []

    def test_list_signers(self, account_id):
        """Test 4: Listar signatários"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/signers",
                timeout=10
            )
            data = response.json()

            if response.status_code == 200:
                signers = data.get("data", [])
                self.log("Listar signatários", True, f"Encontrados: {len(signers)}")
                return signers
            else:
                self.log("Listar signatários", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log("Listar signatários", False, f"Erro: {str(e)}")
            return []

    def test_list_templates(self, account_id):
        """Test 5: Listar templates"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/templates",
                timeout=10
            )
            data = response.json()

            if response.status_code == 200:
                templates = data.get("data", [])
                self.log("Listar templates", True, f"Encontrados: {len(templates)}")
                return templates
            else:
                self.log("Listar templates", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log("Listar templates", False, f"Erro: {str(e)}")
            return []

    def test_list_webhooks(self, account_id):
        """Test 6: Listar webhooks"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/webhooks/subscriptions",
                timeout=10
            )
            data = response.json()

            if response.status_code == 200:
                webhooks = data.get("data", [])
                self.log("Listar webhooks", True, f"Encontrados: {len(webhooks)}")
                return webhooks
            else:
                self.log("Listar webhooks", False, f"Status: {response.status_code}")
                return []
        except Exception as e:
            self.log("Listar webhooks", False, f"Erro: {str(e)}")
            return []

    def test_response_format(self, account_id):
        """Test 7: Validar formato de resposta"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 1},
                timeout=10
            )
            data = response.json()

            # Verificar estrutura esperada
            checks = [
                ("status" in data, "Campo 'status' presente"),
                ("message" in data or data.get("status") == 200, "Campo 'message' presente ou status 200"),
                ("data" in data, "Campo 'data' presente"),
            ]

            all_passed = all(check[0] for check in checks)
            details = ", ".join(check[1] for check in checks if check[0])

            self.log("Validar formato de resposta", all_passed, details)
            return all_passed
        except Exception as e:
            self.log("Validar formato de resposta", False, f"Erro: {str(e)}")
            return False

    def test_pagination(self, account_id):
        """Test 8: Testar paginação"""
        try:
            # Primeira página
            response1 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 5},
                timeout=10
            )

            # Segunda página
            response2 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 2, "per-page": 5},
                timeout=10
            )

            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                docs1 = data1.get("data", [])
                docs2 = data2.get("data", [])

                # Verificar se são diferentes (paginação funcionando)
                different = len(docs1) > 0 and (docs1 != docs2 or len(docs2) == 0)
                self.log("Testar paginação", different, f"Página 1: {len(docs1)} docs, Página 2: {len(docs2)} docs")
                return different
            else:
                self.log("Testar paginação", False, f"Status: {response1.status_code}, {response2.status_code}")
                return False
        except Exception as e:
            self.log("Testar paginação", False, f"Erro: {str(e)}")
            return False

    def test_search(self, account_id):
        """Test 9: Testar busca full-text"""
        try:
            # Buscar sem termo
            response1 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 10, "search": ""},
                timeout=10
            )

            # Buscar com termo (provavelmente retornará menos)
            response2 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 10, "search": "test"},
                timeout=10
            )

            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                docs1 = data1.get("data", [])
                docs2 = data2.get("data", [])

                self.log("Testar busca full-text", True, f"Sem busca: {len(docs1)}, Com busca: {len(docs2)}")
                return True
            else:
                self.log("Testar busca full-text", False, f"Status: {response1.status_code}, {response2.status_code}")
                return False
        except Exception as e:
            self.log("Testar busca full-text", False, f"Erro: {str(e)}")
            return False

    def run_all_tests(self):
        """Executar todos os testes E2E"""
        print("\n" + "="*60)
        print("🧪 TESTE E2E - API Assinafy")
        print("="*60 + "\n")

        # Test 1: Autenticação
        if not self.test_authenticate():
            print("\n❌ Falha na autenticação. Verifique a API Key.")
            return

        # Test 2-6: Listar recursos
        accounts = self.test_list_accounts()
        if not accounts:
            print("\n⚠️  Nenhuma conta encontrada. Usando workspace ID do .env")
            account_id = WORKSPACE_ID
        else:
            account_id = accounts[0].get("id") if isinstance(accounts[0], dict) else WORKSPACE_ID

        print(f"\n📁 Usando account_id: {account_id}\n")

        self.test_list_documents(account_id)
        self.test_list_signers(account_id)
        self.test_list_templates(account_id)
        self.test_list_webhooks(account_id)

        # Test 7-9: Validações
        self.test_response_format(account_id)
        self.test_pagination(account_id)
        self.test_search(account_id)

        # Resumo final
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60 + "\n")

        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)

        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")

        print(f"\n📈 Resultado: {passed}/{total} testes passaram ({passed*100//total}%)")

        if passed == total:
            print("\n🎉 Todos os testes passaram!")
        else:
            print(f"\n⚠️  {total - passed} teste(s) falharam")


if __name__ == "__main__":
    tester = AssinafyE2ETest()
    tester.run_all_tests()
