import pytest
import json
import csv
import tempfile
import os
import zipfile
from datetime import datetime
from report_bundle import ReportBundleGenerator, RunConfig

class TestReportBundle:
    """Test cases for the Report Bundle functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directories for testing
        self.temp_output_dir = tempfile.mkdtemp()
        self.generator = ReportBundleGenerator(self.temp_output_dir)
        
        # Create test images
        self.test_images = []
        for i in range(3):
            image_path = os.path.join(self.temp_output_dir, f"test_image_{i}.png")
            with open(image_path, 'w') as f:
                f.write(f"fake image data {i}")
            self.test_images.append(f"test_image_{i}.png")
    
    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_output_dir):
            shutil.rmtree(self.temp_output_dir)
    
    def test_required_csv_columns_exist(self):
        """Test that CSV has all required columns"""
        # Create test runs
        test_runs = [
            RunConfig(
                run_id="test-run-1",
                timestamp=datetime.now().isoformat(),
                model="test-model.safetensors",
                vae=None,
                loras=[],
                controlnets=[],
                prompt="test prompt 1",
                negative_prompt="test negative 1",
                seed=12345,
                sampler="euler",
                steps=20,
                cfg_scale=7.0,
                width=512,
                height=512,
                batch_size=1,
                batch_count=1,
                workflow={},
                version="1.0.0",
                generated_images=self.test_images[:1],
                generation_type="txt2img"
            ),
            RunConfig(
                run_id="test-run-2",
                timestamp=datetime.now().isoformat(),
                model="test-model-2.safetensors",
                vae="test-vae.safetensors",
                loras=[{"name": "test-lora", "strength": 0.8}],
                controlnets=[{"model": "test-controlnet", "strength": 1.0, "enabled": True}],
                prompt="test prompt 2",
                negative_prompt="test negative 2",
                seed=67890,
                sampler="dpm++",
                steps=30,
                cfg_scale=8.5,
                width=768,
                height=768,
                batch_size=2,
                batch_count=3,
                workflow={"test": "workflow"},
                version="1.0.0",
                generated_images=self.test_images[1:],
                generation_type="img2img"
            )
        ]
        
        # Generate CSV
        csv_path = self.generator.generate_csv(test_runs)
        
        # Validate schema
        assert self.generator.validate_csv_schema(csv_path)
        
        # Check that all required columns exist
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            required_columns = [
                'run_id', 'timestamp', 'model', 'vae', 'prompt', 
                'negative_prompt', 'seed', 'sampler', 'steps', 'cfg_scale',
                'width', 'height', 'batch_size', 'batch_count', 
                'generation_type', 'image_paths', 'loras', 'controlnets', 'workflow_hash'
            ]
            
            for column in required_columns:
                assert column in fieldnames, f"Missing required column: {column}"
        
        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)
    
    def test_empty_values_handled_without_crashes(self):
        """Test that empty values are handled without crashes"""
        # Create test run with empty values
        test_run = RunConfig(
            run_id="",
            timestamp="",
            model="",
            vae=None,
            loras=[],
            controlnets=[],
            prompt="",
            negative_prompt="",
            seed=0,
            sampler="",
            steps=0,
            cfg_scale=0.0,
            width=0,
            height=0,
            batch_size=0,
            batch_count=0,
            workflow={},
            version="",
            generated_images=[],
            generation_type=""
        )
        
        # Should not crash when generating CSV
        csv_path = self.generator.generate_csv([test_run])
        
        # Should not crash when validating schema
        assert self.generator.validate_csv_schema(csv_path)
        
        # Cleanup
        if os.path.exists(csv_path):
            os.remove(csv_path)
    
    def test_csv_schema_validation(self):
        """Test CSV schema validation with valid and invalid schemas"""
        # Test valid CSV
        valid_csv_content = """run_id,timestamp,model,vae,prompt,negative_prompt,seed,sampler,steps,cfg_scale,width,height,batch_size,batch_count,generation_type,image_paths,loras,controlnets,workflow_hash
test-run,2023-01-01T00:00:00,model.safetensors,vae.safetensors,prompt,negative,123,euler,20,7.0,512,512,1,1,txt2img,image.png,[],[],hash123"""
        
        temp_csv = "temp_valid.csv"
        with open(temp_csv, 'w', encoding='utf-8') as f:
            f.write(valid_csv_content)
        
        assert self.generator.validate_csv_schema(temp_csv)
        
        # Test invalid CSV (missing columns)
        invalid_csv_content = """run_id,timestamp,model,prompt,seed
test-run,2023-01-01T00:00:00,model.safetensors,prompt,123"""
        
        temp_csv_invalid = "temp_invalid.csv"
        with open(temp_csv_invalid, 'w', encoding='utf-8') as f:
            f.write(invalid_csv_content)
        
        assert not self.generator.validate_csv_schema(temp_csv_invalid)
        
        # Cleanup
        for temp_file in [temp_csv, temp_csv_invalid]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_image_paths_resolve_to_files(self):
        """Test that all image paths in CSV resolve to files present in zip"""
        # Create test runs with images
        test_runs = [
            RunConfig(
                run_id="test-run-1",
                timestamp=datetime.now().isoformat(),
                model="test-model.safetensors",
                vae=None,
                loras=[],
                controlnets=[],
                prompt="test prompt",
                negative_prompt="",
                seed=12345,
                sampler="euler",
                steps=20,
                cfg_scale=7.0,
                width=512,
                height=512,
                batch_size=1,
                batch_count=1,
                workflow={},
                version="1.0.0",
                generated_images=self.test_images,
                generation_type="txt2img"
            )
        ]
        
        # Mock the registry to return our test runs
        self.generator.registry.runs = {run.run_id: run for run in test_runs}
        
        # Create report bundle
        zip_path = self.generator.create_report_bundle([test_run.run_id for test_run in test_runs])
        
        # Verify zip file exists
        assert os.path.exists(zip_path)
        
        # Extract and verify contents
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Check that results.csv exists
            csv_files = [f for f in zipf.namelist() if f.endswith('results.csv')]
            assert len(csv_files) == 1
            
            # Read CSV and verify image paths
            with zipf.open(csv_files[0]) as csv_file:
                reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
                for row in reader:
                    image_paths = row['image_paths'].split(';') if row['image_paths'] else []
                    for image_path in image_paths:
                        if image_path.strip():
                            # Check that image exists in zip
                            image_in_zip = f"images/{image_path}"
                            assert image_in_zip in zipf.namelist(), f"Image {image_path} not found in zip"
            
            # Check that config.json exists
            config_files = [f for f in zipf.namelist() if f.endswith('config.json')]
            assert len(config_files) == 1
            
            # Check that README.md exists
            readme_files = [f for f in zipf.namelist() if f.endswith('README.md')]
            assert len(readme_files) == 1
        
        # Cleanup
        if os.path.exists(zip_path):
            os.remove(zip_path)
    
    def test_deterministic_file_names_and_paths(self):
        """Test that file names and paths are deterministic"""
        test_runs = [
            RunConfig(
                run_id="test-run-1",
                timestamp=datetime.now().isoformat(),
                model="test-model.safetensors",
                vae=None,
                loras=[],
                controlnets=[],
                prompt="test prompt",
                negative_prompt="",
                seed=12345,
                sampler="euler",
                steps=20,
                cfg_scale=7.0,
                width=512,
                height=512,
                batch_size=1,
                batch_count=1,
                workflow={},
                version="1.0.0",
                generated_images=self.test_images[:1],
                generation_type="txt2img"
            )
        ]
        
        # Mock the registry to return our test runs
        self.generator.registry.runs = {run.run_id: run for run in test_runs}
        
        # Create two report bundles with same data
        zip_path_1 = self.generator.create_report_bundle([test_runs[0].run_id])
        zip_path_2 = self.generator.create_report_bundle([test_runs[0].run_id])
        
        # Verify both zip files exist
        assert os.path.exists(zip_path_1)
        assert os.path.exists(zip_path_2)
        
        # Check that both zips have same structure
        with zipfile.ZipFile(zip_path_1, 'r') as zip1, zipfile.ZipFile(zip_path_2, 'r') as zip2:
            files_1 = sorted(zip1.namelist())
            files_2 = sorted(zip2.namelist())
            
            # Should have same files
            assert files_1 == files_2
            
            # Should have expected file structure
            expected_files = [
                'results.csv',
                'config.json', 
                'README.md',
                'images/test_image_0.png'
            ]
            
            for expected_file in expected_files:
                assert any(f.endswith(expected_file) for f in files_1), f"Missing {expected_file}"
        
        # Cleanup
        for zip_path in [zip_path_1, zip_path_2]:
            if os.path.exists(zip_path):
                os.remove(zip_path)
    
    def test_config_json_structure(self):
        """Test that config.json has correct structure"""
        test_runs = [
            RunConfig(
                run_id="test-run-1",
                timestamp=datetime.now().isoformat(),
                model="test-model.safetensors",
                vae=None,
                loras=[],
                controlnets=[],
                prompt="test prompt",
                negative_prompt="",
                seed=12345,
                sampler="euler",
                steps=20,
                cfg_scale=7.0,
                width=512,
                height=512,
                batch_size=1,
                batch_count=1,
                workflow={},
                version="1.0.0",
                generated_images=self.test_images[:1],
                generation_type="txt2img"
            )
        ]
        
        # Create config.json
        config_path = self.generator.create_config_json(test_runs)
        
        # Verify structure
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Check required top-level keys
        assert 'report_metadata' in config_data
        assert 'runs' in config_data
        
        # Check metadata structure
        metadata = config_data['report_metadata']
        assert 'generated_at' in metadata
        assert 'total_runs' in metadata
        assert 'generation_types' in metadata
        assert 'models_used' in metadata
        
        # Check runs structure
        runs = config_data['runs']
        assert len(runs) == 1
        assert runs[0]['run_id'] == 'test-run-1'
        
        # Cleanup
        if os.path.exists(config_path):
            os.remove(config_path)
    
    def test_readme_content(self):
        """Test that README.md has correct content"""
        test_runs = [
            RunConfig(
                run_id="test-run-1",
                timestamp=datetime.now().isoformat(),
                model="test-model.safetensors",
                vae=None,
                loras=[],
                controlnets=[],
                prompt="test prompt",
                negative_prompt="",
                seed=12345,
                sampler="euler",
                steps=20,
                cfg_scale=7.0,
                width=512,
                height=512,
                batch_size=1,
                batch_count=1,
                workflow={},
                version="1.0.0",
                generated_images=self.test_images[:1],
                generation_type="txt2img"
            )
        ]
        
        # Create README
        readme_path = self.generator.create_readme(test_runs, self.test_images[:1])
        
        # Verify content
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        assert '# Dream Layer Report Bundle' in content
        assert '## Overview' in content
        assert '## Contents' in content
        assert '## Statistics' in content
        assert '## CSV Schema' in content
        assert 'results.csv' in content
        assert 'config.json' in content
        assert 'images/' in content
        assert 'README.md' in content
        
        # Cleanup
        if os.path.exists(readme_path):
            os.remove(readme_path) 