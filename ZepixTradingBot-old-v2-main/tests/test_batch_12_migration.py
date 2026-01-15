"""
Test Suite for Batch 12: Data Migration & Documentation Tools

Tests:
- DataMigrationTool: V4 to V5 migration
- Data integrity verification
- DocGenerator: API documentation generation
- Docstring parsing

Version: 1.0.0
"""

import pytest
import sqlite3
import tempfile
import shutil
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.data_migration_tool import (
    DataMigrationTool,
    MigrationResult,
    MigrationStatus,
    ColumnMapping,
    create_migration_tool
)
from utils.doc_generator import (
    DocGenerator,
    DocstringParser,
    PythonDocExtractor,
    ParameterDoc,
    ReturnDoc,
    FunctionDoc,
    ClassDoc,
    ModuleDoc,
    create_doc_generator,
    generate_service_api_docs
)


class TestMigrationStatus:
    """Test MigrationStatus enum"""
    
    def test_status_values(self):
        """Test all status values exist"""
        assert MigrationStatus.PENDING.value == "PENDING"
        assert MigrationStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert MigrationStatus.COMPLETED.value == "COMPLETED"
        assert MigrationStatus.FAILED.value == "FAILED"
        assert MigrationStatus.ROLLED_BACK.value == "ROLLED_BACK"


class TestMigrationResult:
    """Test MigrationResult dataclass"""
    
    def test_create_result(self):
        """Test creating migration result"""
        result = MigrationResult(
            status=MigrationStatus.COMPLETED,
            source_db="data/trading_bot.db",
            target_db="data/zepix_combined_v3.db",
            records_migrated=100,
            records_failed=2,
            records_skipped=5
        )
        
        assert result.status == MigrationStatus.COMPLETED
        assert result.records_migrated == 100
        assert result.records_failed == 2
        assert result.records_skipped == 5
    
    def test_result_to_dict(self):
        """Test converting result to dictionary"""
        result = MigrationResult(
            status=MigrationStatus.COMPLETED,
            source_db="source.db",
            target_db="target.db",
            records_migrated=50,
            started_at=datetime(2026, 1, 14, 10, 0, 0),
            completed_at=datetime(2026, 1, 14, 10, 5, 0)
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["status"] == "COMPLETED"
        assert result_dict["records_migrated"] == 50
        assert result_dict["started_at"] == "2026-01-14T10:00:00"
        assert result_dict["completed_at"] == "2026-01-14T10:05:00"
    
    def test_result_integrity_fields(self):
        """Test integrity check fields"""
        result = MigrationResult(
            status=MigrationStatus.COMPLETED,
            source_db="source.db",
            target_db="target.db",
            source_total_pnl=1000.50,
            target_total_pnl=1000.50,
            pnl_difference=0.0,
            integrity_check_passed=True
        )
        
        assert result.source_total_pnl == 1000.50
        assert result.target_total_pnl == 1000.50
        assert result.pnl_difference == 0.0
        assert result.integrity_check_passed is True


class TestColumnMapping:
    """Test ColumnMapping dataclass"""
    
    def test_create_mapping(self):
        """Test creating column mapping"""
        mapping = ColumnMapping(
            v4_column="trade_id",
            v5_column="mt5_ticket",
            transform="int"
        )
        
        assert mapping.v4_column == "trade_id"
        assert mapping.v5_column == "mt5_ticket"
        assert mapping.transform == "int"
    
    def test_mapping_with_default(self):
        """Test mapping with default value"""
        mapping = ColumnMapping(
            v4_column="commission",
            v5_column="commission",
            default_value=0.0
        )
        
        assert mapping.default_value == 0.0


class TestDataMigrationTool:
    """Test DataMigrationTool class"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_dir = tempfile.mkdtemp()
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        backup_dir = os.path.join(temp_dir, "backup")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        yield {
            "temp_dir": temp_dir,
            "source_dir": source_dir,
            "target_dir": target_dir,
            "backup_dir": backup_dir
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def v4_database(self, temp_dirs):
        """Create a V4 test database"""
        db_path = os.path.join(temp_dirs["source_dir"], "trading_bot.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                sl_price REAL,
                tp_price REAL,
                lot_size REAL,
                direction TEXT,
                strategy TEXT,
                pnl REAL,
                commission REAL,
                swap REAL,
                comment TEXT,
                status TEXT,
                open_time DATETIME,
                close_time DATETIME,
                chain_id TEXT,
                chain_level INTEGER,
                is_re_entry BOOLEAN,
                order_type TEXT,
                profit_chain_id TEXT,
                profit_level INTEGER DEFAULT 0,
                session_id TEXT,
                sl_adjusted INTEGER DEFAULT 0,
                original_sl_distance REAL DEFAULT 0.0,
                logic_type TEXT,
                base_lot_size REAL DEFAULT 0.0,
                final_lot_size REAL DEFAULT 0.0,
                base_sl_pips REAL DEFAULT 0.0,
                final_sl_pips REAL DEFAULT 0.0,
                lot_multiplier REAL DEFAULT 1.0,
                sl_multiplier REAL DEFAULT 1.0
            )
        """)
        
        test_trades = [
            ("T001", "XAUUSD", 2030.50, 2035.00, 2025.00, 2040.00, 0.10, "BUY", "V3_Combined", 45.00, 0.50, 0.0, "Test trade 1", "closed", "2026-01-10 10:00:00", "2026-01-10 12:00:00", None, 1, 0, "ORDER_A", None, 0, None, 0, 0.0, "LOGIC1", 0.10, 0.10, 25.0, 25.0, 1.0, 1.0),
            ("T002", "XAUUSD", 2028.00, 2020.00, 2035.00, 2015.00, 0.15, "SELL", "V3_Combined", 80.00, 0.75, 0.0, "Test trade 2", "closed", "2026-01-11 09:00:00", "2026-01-11 14:00:00", None, 1, 0, "ORDER_B", None, 0, None, 0, 0.0, "LOGIC2", 0.15, 0.15, 30.0, 30.0, 1.0, 1.0),
            ("T003", "EURUSD", 1.0850, 1.0900, 1.0800, 1.0950, 0.20, "BUY", "V3_Combined", 100.00, 1.00, 0.0, "Test trade 3", "closed", "2026-01-12 08:00:00", "2026-01-12 16:00:00", None, 1, 0, "ORDER_A", None, 0, None, 0, 0.0, "LOGIC1", 0.20, 0.20, 50.0, 50.0, 1.0, 1.0),
        ]
        
        cursor.executemany("""
            INSERT INTO trades (
                trade_id, symbol, entry_price, exit_price, sl_price, tp_price, lot_size, direction,
                strategy, pnl, commission, swap, comment, status, open_time, close_time,
                chain_id, chain_level, is_re_entry, order_type, profit_chain_id, profit_level,
                session_id, sl_adjusted, original_sl_distance, logic_type, base_lot_size, final_lot_size,
                base_sl_pips, final_sl_pips, lot_multiplier, sl_multiplier
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_trades)
        
        conn.commit()
        conn.close()
        
        return db_path
    
    def test_tool_initialization(self, temp_dirs, v4_database):
        """Test tool initialization"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        assert tool.source_db == v4_database
        assert tool.target_dir == temp_dirs["target_dir"]
        assert tool.backup_dir == temp_dirs["backup_dir"]
    
    def test_get_v4_summary(self, temp_dirs, v4_database):
        """Test getting V4 database summary"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        summary = tool.get_v4_summary()
        
        assert summary["total_trades"] == 3
        assert summary["closed_trades"] == 3
        assert summary["total_pnl"] == 225.0
    
    def test_get_v4_trades(self, temp_dirs, v4_database):
        """Test getting V4 trades"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        trades = tool.get_v4_trades()
        
        assert len(trades) == 3
        assert trades[0]["symbol"] in ["XAUUSD", "EURUSD"]
    
    def test_get_v4_trades_with_filter(self, temp_dirs, v4_database):
        """Test getting V4 trades with strategy filter"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        trades = tool.get_v4_trades(strategy_filter="V3")
        
        assert len(trades) == 3
    
    def test_dry_run_migration(self, temp_dirs, v4_database):
        """Test dry run migration"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        result = tool.migrate_to_plugin("v3_combined", dry_run=True)
        
        assert result.status == MigrationStatus.COMPLETED
        assert result.records_migrated == 3
        
        target_db = os.path.join(temp_dirs["target_dir"], "zepix_combined_v3.db")
        assert not os.path.exists(target_db)
    
    def test_actual_migration(self, temp_dirs, v4_database):
        """Test actual migration"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        result = tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        assert result.status == MigrationStatus.COMPLETED
        assert result.records_migrated == 3
        
        target_db = os.path.join(temp_dirs["target_dir"], "zepix_combined_v3.db")
        assert os.path.exists(target_db)
    
    def test_migration_integrity_check(self, temp_dirs, v4_database):
        """Test migration integrity check"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        integrity = tool.verify_integrity("v3_combined")
        
        assert integrity["passed"] is True
        assert any(c["name"] == "record_count" for c in integrity["checks"])
        assert any(c["name"] == "no_duplicates" for c in integrity["checks"])
    
    def test_pnl_integrity(self, temp_dirs, v4_database):
        """Test P&L integrity after migration"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        result = tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        assert result.source_total_pnl == 225.0
        assert result.target_total_pnl == 225.0
        assert result.pnl_difference < 0.01
        assert result.integrity_check_passed is True
    
    def test_rollback_migration(self, temp_dirs, v4_database):
        """Test rollback migration"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        success = tool.rollback_migration("v3_combined")
        
        assert success is True
        
        target_conn = sqlite3.connect(
            os.path.join(temp_dirs["target_dir"], "zepix_combined_v3.db")
        )
        cursor = target_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM trades WHERE migrated_from = 'v4'")
        count = cursor.fetchone()[0]
        target_conn.close()
        
        assert count == 0
    
    def test_migration_history(self, temp_dirs, v4_database):
        """Test migration history tracking"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        tool.migrate_to_plugin("v3_combined", dry_run=True)
        tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        history = tool.get_migration_history()
        
        assert len(history) == 2
    
    def test_format_migration_report(self, temp_dirs, v4_database):
        """Test migration report formatting"""
        tool = DataMigrationTool(
            source_db=v4_database,
            target_dir=temp_dirs["target_dir"],
            backup_dir=temp_dirs["backup_dir"]
        )
        
        result = tool.migrate_to_plugin("v3_combined", dry_run=False)
        report = tool.format_migration_report(result)
        
        assert "Migration Report" in report
        assert "COMPLETED" in report
        assert "Migrated: 3" in report


class TestFactoryFunction:
    """Test factory function"""
    
    def test_create_migration_tool(self):
        """Test create_migration_tool factory"""
        tool = create_migration_tool(
            source_db="data/test.db",
            target_dir="data/test"
        )
        
        assert isinstance(tool, DataMigrationTool)
        assert tool.source_db == "data/test.db"
        assert tool.target_dir == "data/test"


class TestDocstringParser:
    """Test DocstringParser class"""
    
    def test_parse_simple_docstring(self):
        """Test parsing simple docstring"""
        parser = DocstringParser()
        
        docstring = """
        This is a simple description.
        """
        
        result = parser.parse(docstring)
        
        assert "simple description" in result["description"]
    
    def test_parse_google_style_docstring(self):
        """Test parsing Google-style docstring"""
        parser = DocstringParser()
        
        docstring = """
        Calculate lot size for a trade.
        
        Args:
            symbol (str): Trading symbol
            risk_percentage (float): Risk percentage
            stop_loss_pips (float): Stop loss in pips
        
        Returns:
            float: Calculated lot size
        """
        
        result = parser.parse(docstring)
        
        assert "Calculate lot size" in result["description"]
        assert len(result["params"]) == 3
        assert result["params"][0].name == "symbol"
        assert result["params"][0].type_hint == "str"
        assert result["returns"] is not None
    
    def test_parse_empty_docstring(self):
        """Test parsing empty docstring"""
        parser = DocstringParser()
        
        result = parser.parse("")
        
        assert result["description"] == ""
        assert result["params"] == []
        assert result["returns"] is None


class TestParameterDoc:
    """Test ParameterDoc dataclass"""
    
    def test_create_parameter_doc(self):
        """Test creating parameter documentation"""
        param = ParameterDoc(
            name="symbol",
            type_hint="str",
            description="Trading symbol",
            default='"XAUUSD"'
        )
        
        assert param.name == "symbol"
        assert param.type_hint == "str"
        assert param.description == "Trading symbol"
        assert param.default == '"XAUUSD"'


class TestReturnDoc:
    """Test ReturnDoc dataclass"""
    
    def test_create_return_doc(self):
        """Test creating return documentation"""
        ret = ReturnDoc(
            type_hint="float",
            description="Calculated lot size"
        )
        
        assert ret.type_hint == "float"
        assert ret.description == "Calculated lot size"


class TestFunctionDoc:
    """Test FunctionDoc dataclass"""
    
    def test_create_function_doc(self):
        """Test creating function documentation"""
        func = FunctionDoc(
            name="calculate_lot_size",
            docstring="Calculate lot size for a trade.",
            parameters=[
                ParameterDoc(name="symbol", type_hint="str"),
                ParameterDoc(name="risk", type_hint="float")
            ],
            returns=ReturnDoc(type_hint="float"),
            is_async=True
        )
        
        assert func.name == "calculate_lot_size"
        assert func.is_async is True
        assert len(func.parameters) == 2
    
    def test_function_to_markdown(self):
        """Test converting function to markdown"""
        func = FunctionDoc(
            name="test_func",
            docstring="Test function description.",
            parameters=[
                ParameterDoc(name="arg1", type_hint="str", description="First argument")
            ],
            returns=ReturnDoc(type_hint="bool", description="Success status")
        )
        
        md = func.to_markdown()
        
        assert "test_func" in md
        assert "arg1" in md
        assert "str" in md
        assert "bool" in md


class TestClassDoc:
    """Test ClassDoc dataclass"""
    
    def test_create_class_doc(self):
        """Test creating class documentation"""
        cls = ClassDoc(
            name="OrderService",
            docstring="Service for order management.",
            base_classes=["BaseService"],
            methods=[
                FunctionDoc(name="place_order", docstring="Place an order.")
            ]
        )
        
        assert cls.name == "OrderService"
        assert len(cls.base_classes) == 1
        assert len(cls.methods) == 1
    
    def test_class_to_markdown(self):
        """Test converting class to markdown"""
        cls = ClassDoc(
            name="TestClass",
            docstring="Test class description.",
            base_classes=["BaseClass"],
            methods=[
                FunctionDoc(name="test_method", docstring="Test method.")
            ]
        )
        
        md = cls.to_markdown()
        
        assert "TestClass" in md
        assert "BaseClass" in md
        assert "test_method" in md


class TestModuleDoc:
    """Test ModuleDoc dataclass"""
    
    def test_create_module_doc(self):
        """Test creating module documentation"""
        module = ModuleDoc(
            name="order_service",
            path="src/services/order_service.py",
            docstring="Order service module.",
            classes=[
                ClassDoc(name="OrderService", docstring="Order service class.")
            ]
        )
        
        assert module.name == "order_service"
        assert len(module.classes) == 1
    
    def test_module_to_markdown(self):
        """Test converting module to markdown"""
        module = ModuleDoc(
            name="test_module",
            path="src/test_module.py",
            docstring="Test module description.",
            classes=[
                ClassDoc(name="TestClass", docstring="Test class.")
            ]
        )
        
        md = module.to_markdown()
        
        assert "test_module" in md
        assert "src/test_module.py" in md
        assert "TestClass" in md


class TestPythonDocExtractor:
    """Test PythonDocExtractor class"""
    
    @pytest.fixture
    def temp_python_file(self):
        """Create temporary Python file for testing"""
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, "test_module.py")
        
        content = '''
"""
Test module docstring.

This module provides test functionality.
"""

from typing import Optional

class TestService:
    """
    Test service class.
    
    Provides test methods.
    """
    
    def __init__(self, config: dict):
        """Initialize service."""
        self.config = config
    
    async def process_data(self, data: str, timeout: float = 30.0) -> bool:
        """
        Process input data.
        
        Args:
            data (str): Input data to process
            timeout (float): Processing timeout
        
        Returns:
            bool: True if successful
        """
        return True


def helper_function(value: int) -> str:
    """
    Helper function.
    
    Args:
        value (int): Input value
    
    Returns:
        str: String representation
    """
    return str(value)
'''
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        yield file_path
        
        shutil.rmtree(temp_dir)
    
    def test_extract_from_file(self, temp_python_file):
        """Test extracting documentation from file"""
        extractor = PythonDocExtractor()
        
        module_doc = extractor.extract_from_file(temp_python_file)
        
        assert module_doc.name == "test_module"
        assert "Test module docstring" in module_doc.docstring
        assert len(module_doc.classes) == 1
        assert len(module_doc.functions) == 1
    
    def test_extract_class(self, temp_python_file):
        """Test extracting class documentation"""
        extractor = PythonDocExtractor()
        
        module_doc = extractor.extract_from_file(temp_python_file)
        
        cls = module_doc.classes[0]
        assert cls.name == "TestService"
        assert "Test service class" in cls.docstring
        assert len(cls.methods) >= 2
    
    def test_extract_async_method(self, temp_python_file):
        """Test extracting async method"""
        extractor = PythonDocExtractor()
        
        module_doc = extractor.extract_from_file(temp_python_file)
        
        cls = module_doc.classes[0]
        process_method = next(
            (m for m in cls.methods if m.name == "process_data"),
            None
        )
        
        assert process_method is not None
        assert process_method.is_async is True
    
    def test_extract_function_parameters(self, temp_python_file):
        """Test extracting function parameters"""
        extractor = PythonDocExtractor()
        
        module_doc = extractor.extract_from_file(temp_python_file)
        
        helper = module_doc.functions[0]
        assert helper.name == "helper_function"
        assert len(helper.parameters) == 1
        assert helper.parameters[0].name == "value"
        assert helper.parameters[0].type_hint == "int"


class TestDocGenerator:
    """Test DocGenerator class"""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure"""
        temp_dir = tempfile.mkdtemp()
        
        src_dir = os.path.join(temp_dir, "src")
        services_dir = os.path.join(src_dir, "core", "services")
        output_dir = os.path.join(temp_dir, "docs", "api")
        
        os.makedirs(services_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        service_content = '''
"""
Order Execution Service

Provides order management functionality.
"""

class OrderService:
    """Order service class."""
    
    async def place_order(self, symbol: str, direction: str) -> int:
        """
        Place a new order.
        
        Args:
            symbol (str): Trading symbol
            direction (str): BUY or SELL
        
        Returns:
            int: Order ticket number
        """
        return 12345
'''
        
        with open(os.path.join(services_dir, "order_service.py"), 'w') as f:
            f.write(service_content)
        
        yield {
            "temp_dir": temp_dir,
            "src_dir": src_dir,
            "services_dir": services_dir,
            "output_dir": output_dir
        }
        
        shutil.rmtree(temp_dir)
    
    def test_generator_initialization(self, temp_project):
        """Test generator initialization"""
        generator = DocGenerator(
            source_dir=temp_project["src_dir"],
            output_dir=temp_project["output_dir"]
        )
        
        assert generator.source_dir == temp_project["src_dir"]
        assert generator.output_dir == temp_project["output_dir"]
    
    def test_generate_file(self, temp_project):
        """Test generating documentation for single file"""
        generator = DocGenerator(
            source_dir=temp_project["src_dir"],
            output_dir=temp_project["output_dir"]
        )
        
        service_file = os.path.join(
            temp_project["services_dir"],
            "order_service.py"
        )
        
        output_path = generator.generate_file(service_file)
        
        assert os.path.exists(output_path)
        
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert "OrderService" in content
        assert "place_order" in content
    
    def test_generate_service_api_docs(self, temp_project):
        """Test generating service API documentation"""
        generator = DocGenerator(
            source_dir=temp_project["src_dir"],
            output_dir=temp_project["output_dir"]
        )
        
        output_path = generator.generate_service_api_docs()
        
        assert os.path.exists(output_path)
        assert output_path.endswith("service_api.md")
        
        with open(output_path, 'r') as f:
            content = f.read()
        
        assert "Service API Documentation" in content
    
    def test_generate_all(self, temp_project):
        """Test generating all documentation"""
        generator = DocGenerator(
            source_dir=temp_project["src_dir"],
            output_dir=temp_project["output_dir"]
        )
        
        results = generator.generate_all()
        
        assert "services" in results
        assert len(results["services"]) >= 1


class TestDocGeneratorFactory:
    """Test doc generator factory functions"""
    
    def test_create_doc_generator(self):
        """Test create_doc_generator factory"""
        generator = create_doc_generator(
            source_dir="src",
            output_dir="docs/api"
        )
        
        assert isinstance(generator, DocGenerator)
        assert generator.source_dir == "src"
        assert generator.output_dir == "docs/api"


class TestIntegration:
    """Integration tests for migration and documentation"""
    
    @pytest.fixture
    def full_test_environment(self):
        """Create full test environment"""
        temp_dir = tempfile.mkdtemp()
        
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        backup_dir = os.path.join(temp_dir, "backup")
        docs_dir = os.path.join(temp_dir, "docs", "api")
        
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)
        
        db_path = os.path.join(source_dir, "trading_bot.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE trades (
                id INTEGER PRIMARY KEY,
                trade_id TEXT,
                symbol TEXT,
                entry_price REAL,
                exit_price REAL,
                sl_price REAL,
                tp_price REAL,
                lot_size REAL,
                direction TEXT,
                strategy TEXT,
                pnl REAL,
                commission REAL DEFAULT 0,
                swap REAL DEFAULT 0,
                comment TEXT,
                status TEXT,
                open_time DATETIME,
                close_time DATETIME,
                chain_id TEXT,
                chain_level INTEGER DEFAULT 1,
                is_re_entry BOOLEAN DEFAULT 0,
                order_type TEXT,
                profit_chain_id TEXT,
                profit_level INTEGER DEFAULT 0,
                session_id TEXT,
                sl_adjusted INTEGER DEFAULT 0,
                original_sl_distance REAL DEFAULT 0.0,
                logic_type TEXT,
                base_lot_size REAL DEFAULT 0.0,
                final_lot_size REAL DEFAULT 0.0,
                base_sl_pips REAL DEFAULT 0.0,
                final_sl_pips REAL DEFAULT 0.0,
                lot_multiplier REAL DEFAULT 1.0,
                sl_multiplier REAL DEFAULT 1.0
            )
        """)
        
        for i in range(10):
            cursor.execute("""
                INSERT INTO trades (trade_id, symbol, entry_price, exit_price, sl_price, tp_price,
                    lot_size, direction, strategy, pnl, status, open_time, close_time, logic_type, order_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"T{i:03d}",
                "XAUUSD",
                2030.0 + i,
                2035.0 + i,
                2025.0 + i,
                2040.0 + i,
                0.10,
                "BUY" if i % 2 == 0 else "SELL",
                "V3_Combined",
                50.0 + i * 10,
                "closed",
                f"2026-01-{10+i} 10:00:00",
                f"2026-01-{10+i} 12:00:00",
                "LOGIC1",
                "ORDER_A" if i % 2 == 0 else "ORDER_B"
            ))
        
        conn.commit()
        conn.close()
        
        yield {
            "temp_dir": temp_dir,
            "source_dir": source_dir,
            "target_dir": target_dir,
            "backup_dir": backup_dir,
            "docs_dir": docs_dir,
            "db_path": db_path
        }
        
        shutil.rmtree(temp_dir)
    
    def test_full_migration_workflow(self, full_test_environment):
        """Test complete migration workflow"""
        env = full_test_environment
        
        tool = DataMigrationTool(
            source_db=env["db_path"],
            target_dir=env["target_dir"],
            backup_dir=env["backup_dir"]
        )
        
        summary = tool.get_v4_summary()
        assert summary["total_trades"] == 10
        
        dry_result = tool.migrate_to_plugin("v3_combined", dry_run=True)
        assert dry_result.status == MigrationStatus.COMPLETED
        assert dry_result.records_migrated == 10
        
        result = tool.migrate_to_plugin("v3_combined", dry_run=False)
        assert result.status == MigrationStatus.COMPLETED
        assert result.records_migrated == 10
        
        integrity = tool.verify_integrity("v3_combined")
        assert integrity["passed"] is True
        
        expected_pnl = sum(50.0 + i * 10 for i in range(10))
        assert result.source_total_pnl == expected_pnl
        assert result.integrity_check_passed is True
    
    def test_migration_with_rollback(self, full_test_environment):
        """Test migration with rollback"""
        env = full_test_environment
        
        tool = DataMigrationTool(
            source_db=env["db_path"],
            target_dir=env["target_dir"],
            backup_dir=env["backup_dir"]
        )
        
        tool.migrate_to_plugin("v3_combined", dry_run=False)
        
        integrity_before = tool.verify_integrity("v3_combined")
        assert integrity_before["passed"] is True
        
        success = tool.rollback_migration("v3_combined")
        assert success is True
        
        integrity_after = tool.verify_integrity("v3_combined")
        migrated_check = next(
            (c for c in integrity_after["checks"] if c["name"] == "migrated_records"),
            None
        )
        assert migrated_check is not None
        assert migrated_check["value"] == 0


class TestBackwardCompatibility:
    """Test backward compatibility"""
    
    def test_migration_tool_handles_missing_columns(self):
        """Test migration tool handles missing V4 columns gracefully"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            db_path = os.path.join(temp_dir, "trading_bot.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE trades (
                    id INTEGER PRIMARY KEY,
                    trade_id TEXT,
                    symbol TEXT,
                    entry_price REAL,
                    lot_size REAL,
                    direction TEXT,
                    pnl REAL,
                    status TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO trades (trade_id, symbol, entry_price, lot_size, direction, pnl, status)
                VALUES ('T001', 'XAUUSD', 2030.0, 0.10, 'BUY', 50.0, 'closed')
            """)
            
            conn.commit()
            conn.close()
            
            tool = DataMigrationTool(
                source_db=db_path,
                target_dir=temp_dir,
                backup_dir=temp_dir
            )
            
            result = tool.migrate_to_plugin("test_plugin", dry_run=False)
            
            assert result.status == MigrationStatus.COMPLETED
            assert result.records_migrated == 1
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_doc_generator_handles_syntax_errors(self):
        """Test doc generator handles syntax errors gracefully"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            bad_file = os.path.join(temp_dir, "bad_syntax.py")
            with open(bad_file, 'w') as f:
                f.write("def broken(:\n    pass\n")
            
            extractor = PythonDocExtractor()
            module_doc = extractor.extract_from_file(bad_file)
            
            assert "Error parsing file" in module_doc.docstring
            
        finally:
            shutil.rmtree(temp_dir)
