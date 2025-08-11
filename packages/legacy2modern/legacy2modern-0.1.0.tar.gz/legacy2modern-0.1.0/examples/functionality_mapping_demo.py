#!/usr/bin/env python3
"""
Functionality Mapping System Demo

This script demonstrates the comprehensive functionality mapping system
for software modernization, including COBOL to Python and website modernization.
"""

import json
import sys
import os
from datetime import datetime

# Add the engine directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.functionality_mapper import (
    FunctionalityMapper, FunctionalityType, EquivalenceLevel
)
from engine.modernizers.cobol_system.functionality_mapper import (
    COBOLFunctionalityMapper, COBOLDataType
)
from engine.modernizers.static_site.functionality_mapper import (
    WebsiteFunctionalityMapper, WebsiteFramework, UIComponentType
)


def demo_cobol_functionality_mapping():
    """Demonstrate COBOL to Python functionality mapping."""
    print("\n" + "="*60)
    print("COBOL TO PYTHON FUNCTIONALITY MAPPING DEMO")
    print("="*60)
    
    # Create COBOL functionality mapper
    cobol_mapper = COBOLFunctionalityMapper()
    
    # Sample COBOL program
    cobol_source = """
    IDENTIFICATION DIVISION.
    PROGRAM-ID. PAYROLL-PROGRAM.
    
    ENVIRONMENT DIVISION.
    INPUT-OUTPUT SECTION.
    FILE-CONTROL.
        SELECT EMPLOYEE-FILE ASSIGN TO "employees.dat".
        SELECT PAYROLL-FILE ASSIGN TO "payroll.dat".
    
    DATA DIVISION.
    FILE SECTION.
    FD EMPLOYEE-FILE.
    01 EMPLOYEE-RECORD.
        05 EMPLOYEE-ID PIC 9(5).
        05 EMPLOYEE-NAME PIC X(30).
        05 EMPLOYEE-SALARY PIC 9(8)V99.
        05 EMPLOYEE-TAX-RATE PIC V999.
    
    WORKING-STORAGE SECTION.
    01 WS-TOTAL-SALARY PIC 9(10)V99 VALUE ZERO.
    01 WS-TOTAL-TAX PIC 9(10)V99 VALUE ZERO.
    
    PROCEDURE DIVISION.
    MAIN-LOGIC.
        PERFORM INITIALIZE-PROGRAM.
        PERFORM PROCESS-EMPLOYEES.
        PERFORM CALCULATE-TOTALS.
        PERFORM DISPLAY-RESULTS.
        STOP RUN.
    
    INITIALIZE-PROGRAM.
        OPEN INPUT EMPLOYEE-FILE.
        OPEN OUTPUT PAYROLL-FILE.
    
    PROCESS-EMPLOYEES.
        READ EMPLOYEE-FILE.
        PERFORM UNTIL EMPLOYEE-FILE-EOF
            PERFORM CALCULATE-EMPLOYEE-PAYROLL
            READ EMPLOYEE-FILE
        END-PERFORM.
    
    CALCULATE-EMPLOYEE-PAYROLL.
        COMPUTE EMPLOYEE-TAX = EMPLOYEE-SALARY * EMPLOYEE-TAX-RATE.
        COMPUTE EMPLOYEE-NET = EMPLOYEE-SALARY - EMPLOYEE-TAX.
        ADD EMPLOYEE-SALARY TO WS-TOTAL-SALARY.
        ADD EMPLOYEE-TAX TO WS-TOTAL-TAX.
        WRITE PAYROLL-RECORD FROM EMPLOYEE-RECORD.
    
    CALCULATE-TOTALS.
        DISPLAY "TOTAL SALARY: " WS-TOTAL-SALARY.
        DISPLAY "TOTAL TAX: " WS-TOTAL-TAX.
    
    DISPLAY-RESULTS.
        CLOSE EMPLOYEE-FILE.
        CLOSE PAYROLL-FILE.
    """
    
    # Create COBOL program mapping
    functionality_mapping, cobol_mapping = cobol_mapper.create_cobol_program_mapping(
        "PAYROLL-PROGRAM",
        "payroll_program",
        cobol_source
    )
    
    print(f"Created functionality mapping: {functionality_mapping.functionality_id}")
    print(f"COBOL Program: {cobol_mapping.program_name}")
    print(f"Python Module: {cobol_mapping.python_module_name}")
    
    # Analyze COBOL structure
    analysis = cobol_mapper.analyze_cobol_structure(
        functionality_mapping.functionality_id,
        cobol_source
    )
    
    print(f"\nCOBOL Structure Analysis:")
    print(f"  Divisions: {list(analysis['divisions'].keys())}")
    print(f"  Paragraphs: {analysis['paragraphs']}")
    print(f"  Files: {analysis['files']}")
    print(f"  Fields: {len(analysis['fields'])} field definitions")
    
    # Map COBOL fields
    field_definitions = [
        {"name": "EMPLOYEE-ID", "level": 5, "pic": "PIC 9(5)"},
        {"name": "EMPLOYEE-NAME", "level": 5, "pic": "PIC X(30)"},
        {"name": "EMPLOYEE-SALARY", "level": 5, "pic": "PIC 9(8)V99"},
        {"name": "EMPLOYEE-TAX-RATE", "level": 5, "pic": "PIC V999"},
        {"name": "WS-TOTAL-SALARY", "level": 1, "pic": "PIC 9(10)V99"},
        {"name": "WS-TOTAL-TAX", "level": 1, "pic": "PIC 9(10)V99"}
    ]
    
    field_mappings = cobol_mapper.map_cobol_fields(
        functionality_mapping.functionality_id,
        field_definitions
    )
    
    print(f"\nCOBOL Field Mappings:")
    for field in field_mappings:
        print(f"  {field.cobol_name} ({field.cobol_type}) -> {field.python_name} ({field.python_type})")
    
    # Map COBOL paragraphs to Python functions
    paragraph_mappings = {
        "MAIN-LOGIC": "main_logic",
        "INITIALIZE-PROGRAM": "initialize_program",
        "PROCESS-EMPLOYEES": "process_employees",
        "CALCULATE-EMPLOYEE-PAYROLL": "calculate_employee_payroll",
        "CALCULATE-TOTALS": "calculate_totals",
        "DISPLAY-RESULTS": "display_results"
    }
    
    cobol_mapper.map_cobol_paragraphs(
        functionality_mapping.functionality_id,
        paragraph_mappings
    )
    
    print(f"\nCOBOL Paragraph Mappings:")
    for cobol_para, python_func in paragraph_mappings.items():
        print(f"  {cobol_para} -> {python_func}")
    
    # Map file operations
    file_mappings = {
        "EMPLOYEE-FILE": "employees.dat",
        "PAYROLL-FILE": "payroll.dat"
    }
    
    cobol_mapper.map_cobol_files(
        functionality_mapping.functionality_id,
        file_mappings
    )
    
    print(f"\nCOBOL File Mappings:")
    for cobol_file, python_file in file_mappings.items():
        print(f"  {cobol_file} -> {python_file}")
    
    # Map inputs and outputs
    cobol_mapper.map_inputs_outputs(
        functionality_mapping.functionality_id,
        source_inputs={
            "employee_file": "EMPLOYEE-FILE",
            "payroll_file": "PAYROLL-FILE"
        },
        target_inputs={
            "employee_file": "str",
            "payroll_file": "str"
        },
        source_outputs={
            "total_salary": "WS-TOTAL-SALARY",
            "total_tax": "WS-TOTAL-TAX"
        },
        target_outputs={
            "total_salary": "decimal.Decimal",
            "total_tax": "decimal.Decimal"
        },
        data_transformations={
            "employee_id": "int(employee_id)",
            "employee_salary": "decimal.Decimal(employee_salary)",
            "employee_tax_rate": "decimal.Decimal(employee_tax_rate)"
        }
    )
    
    # Map business logic
    cobol_mapper.map_business_logic(
        functionality_mapping.functionality_id,
        source_logic="""
        IF EMPLOYEE-SALARY > 100000 THEN
            COMPUTE EMPLOYEE-TAX-RATE = 0.25
        ELSE
            COMPUTE EMPLOYEE-TAX-RATE = 0.15
        END-IF
        COMPUTE EMPLOYEE-TAX = EMPLOYEE-SALARY * EMPLOYEE-TAX-RATE
        """,
        target_logic="""
        if employee_salary > 100000:
            employee_tax_rate = decimal.Decimal('0.25')
        else:
            employee_tax_rate = decimal.Decimal('0.15')
        employee_tax = employee_salary * employee_tax_rate
        """,
        business_rules=[
            "Tax rate is 25% for salaries over 100,000",
            "Tax rate is 15% for salaries 100,000 and below",
            "Tax is calculated as salary * tax_rate"
        ],
        decision_points=[
            "employee_salary > 100000"
        ],
        error_handling={
            "FILE-NOT-FOUND": "FileNotFoundError",
            "INVALID-DATA": "ValueError",
            "DIVISION-BY-ZERO": "ZeroDivisionError"
        }
    )
    
    # Validate equivalence
    validation_result = cobol_mapper.validate_equivalence(
        functionality_mapping.functionality_id
    )
    
    print(f"\nEquivalence Validation:")
    print(f"  Confidence Score: {validation_result['confidence_score']:.2f}")
    print(f"  Validation Status: {validation_result.get('validation_status', 'unknown')}")
    print(f"  Issues: {len(validation_result.get('issues', []))}")
    print(f"  Warnings: {len(validation_result.get('warnings', []))}")
    
    # Generate test cases
    test_cases = cobol_mapper.generate_python_equivalence_tests(
        functionality_mapping.functionality_id
    )
    
    print(f"\nGenerated {len(test_cases)} test cases for equivalence validation")
    
    return cobol_mapper


def demo_website_functionality_mapping():
    """Demonstrate website modernization functionality mapping."""
    print("\n" + "="*60)
    print("WEBSITE MODERNIZATION FUNCTIONALITY MAPPING DEMO")
    print("="*60)
    
    # Create website functionality mapper
    website_mapper = WebsiteFunctionalityMapper()
    
    # Sample legacy HTML
    legacy_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legacy Company Website</title>
        <link rel="stylesheet" href="bootstrap.css">
        <script src="jquery.js"></script>
    </head>
    <body>
        <nav class="navbar navbar-default">
            <div class="container">
                <div class="navbar-header">
                    <a class="navbar-brand" href="/">Company Name</a>
                </div>
                <ul class="nav navbar-nav">
                    <li><a href="/">Home</a></li>
                    <li><a href="/about">About</a></li>
                    <li><a href="/contact">Contact</a></li>
                </ul>
            </div>
        </nav>
        
        <div class="container">
            <div class="row">
                <div class="col-md-8">
                    <h1>Welcome to Our Company</h1>
                    <p>This is a legacy website that needs modernization.</p>
                    
                    <form id="contact-form" action="/api/contact" method="post">
                        <div class="form-group">
                            <label for="name">Name:</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email:</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="message">Message:</label>
                            <textarea class="form-control" id="message" name="message" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Send Message</button>
                    </form>
                </div>
                
                <div class="col-md-4">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Contact Information</h3>
                        </div>
                        <div class="panel-body">
                            <p><strong>Email:</strong> info@company.com</p>
                            <p><strong>Phone:</strong> (555) 123-4567</p>
                            <p><strong>Address:</strong> 123 Main St, City, State</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 Company Name. All rights reserved.</p>
            </div>
        </footer>
        
        <script>
        $(document).ready(function() {
            $('#contact-form').on('submit', function(e) {
                e.preventDefault();
                $.ajax({
                    url: '/api/contact',
                    method: 'POST',
                    data: $(this).serialize(),
                    success: function(response) {
                        alert('Message sent successfully!');
                    },
                    error: function(xhr) {
                        alert('Error sending message: ' + xhr.responseText);
                    }
                });
            });
        });
        </script>
    </body>
    </html>
    """
    
    # Create website mapping
    functionality_mapping, website_mapping = website_mapper.create_website_mapping(
        "https://legacy-company.com",
        "https://modern-company.com",
        WebsiteFramework.REACT,
        legacy_html
    )
    
    print(f"Created functionality mapping: {functionality_mapping.functionality_id}")
    print(f"Legacy URL: {website_mapping.legacy_url}")
    print(f"Modern URL: {website_mapping.modern_url}")
    print(f"Target Framework: {website_mapping.target_framework.value}")
    
    # Analyze legacy website
    analysis = website_mapper.analyze_legacy_website(
        functionality_mapping.functionality_id,
        legacy_html
    )
    
    print(f"\nLegacy Website Analysis:")
    print(f"  Components: {len(analysis['components'])}")
    print(f"  Forms: {len(analysis['forms'])}")
    print(f"  Tables: {len(analysis['tables'])}")
    print(f"  Navigation: {len(analysis['navigation'])}")
    print(f"  Scripts: {len(analysis['scripts'])}")
    print(f"  Styles: {len(analysis['styles'])}")
    print(f"  Links: {len(analysis['links'])}")
    
    # Map UI components
    component_mappings = [
        {
            "legacy_selector": ".navbar",
            "modern_component": "Navigation",
            "component_type": "navigation",
            "props_mapping": {
                "brand": "Company Name",
                "links": "['Home', 'About', 'Contact']"
            },
            "event_handlers": {
                "onNavClick": "handleNavigation"
            },
            "styling_mapping": {
                "navbar-default": "bg-white shadow-sm",
                "navbar-brand": "text-xl font-bold"
            },
            "accessibility_features": [
                "aria-label for navigation",
                "keyboard navigation support"
            ]
        },
        {
            "legacy_selector": "#contact-form",
            "modern_component": "ContactForm",
            "component_type": "form",
            "props_mapping": {
                "action": "/api/contact",
                "method": "POST"
            },
            "event_handlers": {
                "onSubmit": "handleContactSubmit",
                "onChange": "handleFormChange"
            },
            "styling_mapping": {
                "form-control": "border border-gray-300 rounded px-3 py-2",
                "btn btn-primary": "bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
            },
            "accessibility_features": [
                "form labels",
                "required field indicators",
                "error message announcements"
            ]
        },
        {
            "legacy_selector": ".panel",
            "modern_component": "ContactInfo",
            "component_type": "card",
            "props_mapping": {
                "title": "Contact Information",
                "email": "info@company.com",
                "phone": "(555) 123-4567",
                "address": "123 Main St, City, State"
            },
            "styling_mapping": {
                "panel-default": "bg-white border border-gray-200 rounded-lg shadow",
                "panel-heading": "bg-gray-50 px-4 py-3 border-b",
                "panel-body": "p-4"
            }
        }
    ]
    
    ui_mappings = website_mapper.map_ui_components(
        functionality_mapping.functionality_id,
        component_mappings
    )
    
    print(f"\nUI Component Mappings:")
    for mapping in ui_mappings:
        print(f"  {mapping.legacy_selector} -> {mapping.modern_component} ({mapping.component_type.value})")
    
    # Map API endpoints
    api_mappings = [
        {
            "legacy_endpoint": "/api/contact",
            "modern_endpoint": "/api/contact",
            "http_method": "POST",
            "request_mapping": {
                "name": "name",
                "email": "email",
                "message": "message"
            },
            "response_mapping": {
                "success": "success",
                "message": "message"
            },
            "authentication": {
                "type": "none"
            },
            "error_handling": {
                "400": "Bad Request - Invalid form data",
                "500": "Internal Server Error - Server processing error"
            }
        }
    ]
    
    api_mappings_list = website_mapper.map_api_endpoints(
        functionality_mapping.functionality_id,
        api_mappings
    )
    
    print(f"\nAPI Endpoint Mappings:")
    for api in api_mappings_list:
        print(f"  {api.http_method} {api.legacy_endpoint} -> {api.modern_endpoint}")
    
    # Map routing
    routing_mapping = {
        "/": "/",
        "/about": "/about",
        "/contact": "/contact"
    }
    
    website_mapper.map_routing(
        functionality_mapping.functionality_id,
        routing_mapping
    )
    
    print(f"\nRouting Mappings:")
    for legacy_route, modern_route in routing_mapping.items():
        print(f"  {legacy_route} -> {modern_route}")
    
    # Map state management
    state_mapping = {
        "form_data": "contactFormData",
        "form_errors": "contactFormErrors",
        "is_submitting": "isSubmitting",
        "navigation_state": "navigationState"
    }
    
    website_mapper.map_state_management(
        functionality_mapping.functionality_id,
        state_mapping
    )
    
    print(f"\nState Management Mappings:")
    for legacy_state, modern_state in state_mapping.items():
        print(f"  {legacy_state} -> {modern_state}")
    
    # Generate modernization plan
    plan = website_mapper.generate_modernization_plan(
        functionality_mapping.functionality_id
    )
    
    print(f"\nModernization Plan:")
    print(f"  Target Framework: {plan['target_framework']}")
    print(f"  Components to Create: {plan['components_to_create']}")
    print(f"  API Endpoints to Migrate: {plan['api_endpoints_to_migrate']}")
    print(f"  Routes to Map: {plan['routes_to_map']}")
    print(f"  Estimated Effort: {plan['estimated_effort']}")
    
    print(f"\nRecommendations:")
    for i, recommendation in enumerate(plan['recommendations'][:5], 1):
        print(f"  {i}. {recommendation}")
    
    return website_mapper


def demo_comprehensive_mapping():
    """Demonstrate comprehensive functionality mapping across multiple systems."""
    print("\n" + "="*60)
    print("COMPREHENSIVE FUNCTIONALITY MAPPING DEMO")
    print("="*60)
    
    # Create base functionality mapper
    mapper = FunctionalityMapper()
    
    # Create mappings for different modernization scenarios
    scenarios = [
        {
            "type": FunctionalityType.PROGRAM,
            "source_name": "LEGACY-PAYROLL",
            "target_name": "modern_payroll_system",
            "source_language": "cobol",
            "target_language": "python",
            "description": "Payroll system modernization"
        },
        {
            "type": FunctionalityType.COMPONENT,
            "source_name": "https://legacy-ecommerce.com",
            "target_name": "https://modern-ecommerce.com",
            "source_language": "html",
            "target_language": "react",
            "description": "E-commerce website modernization"
        },
        {
            "type": FunctionalityType.API_ENDPOINT,
            "source_name": "/api/legacy/users",
            "target_name": "/api/v2/users",
            "source_language": "soap",
            "target_language": "rest",
            "description": "API modernization"
        },
        {
            "type": FunctionalityType.BUSINESS_RULE,
            "source_name": "TAX-CALCULATION-RULE",
            "target_name": "tax_calculation_service",
            "source_language": "cobol",
            "target_language": "python",
            "description": "Business rule modernization"
        }
    ]
    
    mappings = []
    for scenario in scenarios:
        mapping = mapper.create_functionality_mapping(
            functionality_type=scenario["type"],
            source_name=scenario["source_name"],
            target_name=scenario["target_name"],
            source_language=scenario["source_language"],
            target_language=scenario["target_language"]
        )
        mappings.append(mapping)
        
        print(f"Created {scenario['description']}: {mapping.functionality_id}")
    
    # Add input/output mappings for each scenario
    for i, mapping in enumerate(mappings):
        if mapping.functionality_type == FunctionalityType.PROGRAM:
            mapper.map_inputs_outputs(
                mapping.functionality_id,
                source_inputs={"employee_data": "COBOL-RECORD"},
                target_inputs={"employee_data": "dict"},
                source_outputs={"payroll_result": "COBOL-RECORD"},
                target_outputs={"payroll_result": "dict"}
            )
        elif mapping.functionality_type == FunctionalityType.COMPONENT:
            mapper.map_inputs_outputs(
                mapping.functionality_id,
                source_inputs={"user_session": "PHP-SESSION"},
                target_inputs={"user_session": "React-Context"},
                source_outputs={"page_content": "HTML"},
                target_outputs={"page_content": "JSX"}
            )
        elif mapping.functionality_type == FunctionalityType.API_ENDPOINT:
            mapper.map_inputs_outputs(
                mapping.functionality_id,
                source_inputs={"soap_request": "XML"},
                target_inputs={"rest_request": "JSON"},
                source_outputs={"soap_response": "XML"},
                target_outputs={"rest_response": "JSON"}
            )
        elif mapping.functionality_type == FunctionalityType.BUSINESS_RULE:
            mapper.map_inputs_outputs(
                mapping.functionality_id,
                source_inputs={"income": "PIC 9(10)V99"},
                target_inputs={"income": "decimal.Decimal"},
                source_outputs={"tax_amount": "PIC 9(10)V99"},
                target_outputs={"tax_amount": "decimal.Decimal"}
            )
    
    # Add business logic mappings
    for i, mapping in enumerate(mappings):
        if mapping.functionality_type == FunctionalityType.BUSINESS_RULE:
            mapper.map_business_logic(
                mapping.functionality_id,
                source_logic="IF INCOME > 50000 THEN TAX-RATE = 0.25 ELSE TAX-RATE = 0.15",
                target_logic="tax_rate = 0.25 if income > 50000 else 0.15",
                business_rules=["Progressive tax system", "Higher rate for higher income"],
                decision_points=["income > 50000"]
            )
    
    # Validate all mappings
    print(f"\nValidating all mappings...")
    for mapping in mappings:
        validation_result = mapper.validate_equivalence(mapping.functionality_id)
        print(f"  {mapping.functionality_id}: {validation_result['confidence_score']:.2f} confidence")
    
    # Get comprehensive summary
    summary = mapper.get_mapping_summary()
    
    print(f"\nComprehensive Mapping Summary:")
    print(f"  Total Mappings: {summary['total_mappings']}")
    print(f"  Validated: {summary['validated_count']}")
    print(f"  Needs Review: {summary['needs_review_count']}")
    print(f"  Failed: {summary['failed_count']}")
    print(f"  Average Confidence: {summary['average_confidence']:.2f}")
    
    print(f"\nBy Type:")
    for type_name, count in summary['type_counts'].items():
        print(f"  {type_name}: {count}")
    
    print(f"\nBy Language Pair:")
    for pair, count in summary['language_pairs'].items():
        print(f"  {pair}: {count}")
    
    # Export mappings
    exported_data = mapper.export_mappings("json")
    print(f"\nExported {len(mapper.mappings)} mappings to JSON format")
    
    return mapper


def main():
    """Run the functionality mapping demos."""
    print("FUNCTIONALITY MAPPING SYSTEM DEMONSTRATION")
    print("="*60)
    print("This demo showcases the comprehensive functionality mapping system")
    print("for software modernization across different scenarios.")
    
    try:
        # Demo COBOL functionality mapping
        cobol_mapper = demo_cobol_functionality_mapping()
        
        # Demo website functionality mapping
        website_mapper = demo_website_functionality_mapping()
        
        # Demo comprehensive mapping
        comprehensive_mapper = demo_comprehensive_mapping()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The functionality mapping system provides:")
        print("✓ Comprehensive mapping between source and target systems")
        print("✓ Input/output equivalence validation")
        print("✓ Business logic preservation")
        print("✓ Specialized mappers for different modernization scenarios")
        print("✓ Validation and confidence scoring")
        print("✓ Export/import capabilities")
        print("✓ Detailed analysis and modernization planning")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 