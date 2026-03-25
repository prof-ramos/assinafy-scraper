#!/usr/bin/env python3
"""
Teste E2E da API Assinafy

Autenticação e testes de ponta a ponta nos principais endpoints.
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Carregar credenciais
load_dotenv()

API_KEY = os.getenv("ASSINAFY_API_KEY")
WORKSPACE_ID = os.getenv("ASSINAFY_WORKSPACE_ID")
BASE_URL = "https://api.assinafy.com.br/v1"

# Validação de credenciais
if not API_KEY:
    print("❌ ERRO: ASSINAFY_API_KEY não encontrado no arquivo .env")
    sys.exit(1)

if not WORKSPACE_ID:
    print("❌ ERRO: ASSINAFY_WORKSPACE_ID não encontrado no arquivo .env")
    sys.exit(1)


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

    def _get_response_details(self, response):
        """Extrair detalhes da resposta para logging de erros"""
        try:
            if response.status_code != 200:
                return f"Status: {response.status_code}, Error: {response.text[:200]}"
        except:
            pass
        return f"Status: {response.status_code}"

    def test_authenticate(self):
        """Test 1: Autenticação com API Key"""
        try:
            response = self.session.get(f"{BASE_URL}/accounts", timeout=10)
            if response.status_code == 200:
                self.log("Autenticação com API Key", True, f"Status: {response.status_code}")
                return True
            else:
                details = self._get_response_details(response)
                self.log("Autenticação com API Key", False, details)
                return False
        except Exception as e:
            self.log("Autenticação com API Key", False, f"Erro: {str(e)}")
            return False

    def test_list_accounts(self):
        """Test 2: Listar contas"""
        try:
            response = self.session.get(f"{BASE_URL}/accounts", timeout=10)

            if response.status_code != 200:
                details = self._get_response_details(response)
                self.log("Listar contas", False, details)
                return []

            data = response.json()

            if "data" in data:
                accounts = data.get("data", [])
                self.log("Listar contas", True, f"Encontradas: {len(accounts)} contas")
                return accounts
            else:
                self.log("Listar contas", False, "Resposta não contém campo 'data'")
                return []
        except Exception as e:
            self.log("Listar contas", False, f"Erro: {str(e)}")
            return []

    def _test_list_resource(self, account_id, resource_name, endpoint):
        """Helper para testar listagem de recursos"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/{endpoint}",
                timeout=10
            )

            if response.status_code != 200:
                details = self._get_response_details(response)
                self.log(f"Listar {resource_name}", False, details)
                return []

            data = response.json()
            items = data.get("data", [])

            self.log(f"Listar {resource_name}", True, f"Encontrados: {len(items)}")
            return items
        except Exception as e:
            self.log(f"Listar {resource_name}", False, f"Erro: {str(e)}")
            return []

    def test_list_documents(self, account_id):
        """Test 3: Listar documentos com paginação"""
        return self._test_list_resource(account_id, "documentos", "documents")

    def test_list_signers(self, account_id):
        """Test 4: Listar signatários"""
        return self._test_list_resource(account_id, "signatários", "signers")

    def test_list_templates(self, account_id):
        """Test 5: Listar templates"""
        return self._test_list_resource(account_id, "templates", "templates")

    def test_list_webhooks(self, account_id):
        """Test 6: Listar webhooks"""
        return self._test_list_resource(account_id, "webhooks", "webhooks/subscriptions")

    def test_response_format(self, account_id):
        """Test 7: Validar formato de resposta"""
        try:
            response = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 1},
                timeout=10
            )
            data = response.json()

            checks = [
                ("status" in data, "Campo 'status' presente"),
                ("message" in data or data.get("status") == 200, "Campo 'message' presente ou status 200"),
                ("data" in data, "Campo 'data' presente"),
            ]

            passed_checks = [check for check in checks if check[0]]
            failed_checks = [check for check in checks if not check[0]]

            all_passed = len(passed_checks) == len(checks)

            if all_passed:
                details = ", ".join(check[1] for check in checks)
            else:
                details = f"✅ {', '.join(check[1] for check in passed_checks)} | ❌ {', '.join(check[1] for check in failed_checks)}"

            self.log("Validar formato de resposta", all_passed, details)
            return all_passed
        except Exception as e:
            self.log("Validar formato de resposta", False, f"Erro: {str(e)}")
            return False

    def test_pagination(self, account_id):
        """Test 8: Testar paginação"""
        try:
            page_size = 5

            # Primeira página
            response1 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": page_size},
                timeout=10
            )

            # Segunda página
            response2 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 2, "per-page": page_size},
                timeout=10
            )

            if response1.status_code != 200 or response2.status_code != 200:
                self.log("Testar paginação", False, f"Status: P1={response1.status_code}, P2={response2.status_code}")
                return False

            data1 = response1.json()
            data2 = response2.json()
            docs1 = data1.get("data", [])
            docs2 = data2.get("data", [])

            total = len(docs1) + len(docs2)

            # Edge cases: sem resultados ou resultados insuficientes
            if total == 0:
                self.log("Testar paginação", False, "Nenhum documento encontrado para testar paginação")
                return False

            if total < page_size + 1:
                self.log("Testar paginação", False, f"Resultados insuficientes ({total} < {page_size + 1}) para validar paginação")
                return False

            # Validar que as páginas são diferentes
            ids1 = {doc.get('id') for doc in docs1 if doc.get('id')}
            ids2 = {doc.get('id') for doc in docs2 if doc.get('id')}

            different = ids1 != ids2 and len(docs2) > 0
            self.log("Testar paginação", different, f"Página 1: {len(docs1)} docs, Página 2: {len(docs2)} docs, IDs diferentes: {different}")
            return different
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

            # Buscar com termo improvável
            response2 = self.session.get(
                f"{BASE_URL}/accounts/{account_id}/documents",
                params={"page": 1, "per-page": 10, "search": "xyz123improbable456"},
                timeout=10
            )

            if response1.status_code != 200 or response2.status_code != 200:
                self.log("Testar busca full-text", False, f"Status: P1={response1.status_code}, P2={response2.status_code}")
                return False

            data1 = response1.json()
            data2 = response2.json()
            docs1 = data1.get("data", [])
            docs2 = data2.get("data", [])

            # Validar que a busca filtrou resultados
            search_filtered = len(docs2) < len(docs1)

            self.log("Testar busca full-text", search_filtered, f"Sem busca: {len(docs1)}, Com busca: {len(docs2)}, Filtrou: {search_filtered}")
            return search_filtered
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

        # Test 2: Listar contas
        accounts = self.test_list_accounts()

        # Obter account_id válido
        if accounts and len(accounts) > 0:
            account_id = accounts[0].get("id") if isinstance(accounts[0], dict) else WORKSPACE_ID
            # Validar account_id
            if not account_id:
                print(f"\n⚠️  ID de conta inválido. Usando workspace ID do .env")
                account_id = WORKSPACE_ID
        else:
            print(f"\n⚠️  Nenhuma conta encontrada. Usando workspace ID do .env")
            account_id = WORKSPACE_ID

        # Validar account_id final
        if not account_id:
            print("\n❌ ERRO: account_id é None ou vazio")
            return

        print(f"\n📁 Usando account_id: {account_id}\n")

        # Test 3-6: Listar recursos
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

        # Evitar ZeroDivisionError
        if total > 0:
            percentage = passed * 100 // total
            print(f"\n📈 Resultado: {passed}/{total} testes passaram ({percentage}%)")
        else:
            print(f"\n📈 Resultado: {passed}/{total} testes passaram (N/A%)")

        if passed == total:
            print("\n🎉 Todos os testes passaram!")
        else:
            print(f"\n⚠️  {total - passed} teste(s) falharam")


if __name__ == "__main__":
    tester = AssinafyE2ETest()
    tester.run_all_tests()
