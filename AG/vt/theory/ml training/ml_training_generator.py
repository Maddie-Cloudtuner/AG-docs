"""
ML Training Data Generator for Virtual Tagging
================================================
Combines both Excel sheets into ML-ready training data.

Output: Training data with features (X) and labels (Y) for:
- Multi-label classification
- Per-tag-key models
- LLM fine-tuning
"""

import pandas as pd
import base64
import re
import json
from typing import Dict, List, Tuple
from collections import defaultdict


class MLTrainingDataGenerator:
    """
    Generates ML training data by combining:
    - restapi.resources (features)
    - cloud_resource_tags_complete (labels/vocabulary)
    """
    
    def __init__(self, schema_path: str, resources_path: str):
        """Load both Excel files"""
        print("Loading data...")
        self.schema_df = pd.read_excel(schema_path)
        self.resources_df = pd.read_excel(resources_path)
        
        # Build schema vocabulary
        self.tag_vocabulary = self._build_vocabulary()
        
        # Decode tag columns
        self.tag_decoder = self._decode_tag_columns()
        
        print(f"Schema: {len(self.schema_df)} definitions")
        print(f"Resources: {len(self.resources_df)} rows")
        print(f"Tag columns: {len(self.tag_decoder)}")
    
    def _build_vocabulary(self) -> Dict[str, Dict]:
        """
        Build vocabulary from schema.
        Returns: {tag_key: {values: [...], category: '...', ...}}
        """
        vocab = {}
        for _, row in self.schema_df.iterrows():
            key = str(row['tag_key'])
            value = str(row['tag_value'])
            category = str(row['tag_category'])
            
            if key not in vocab:
                vocab[key] = {
                    'values': [],
                    'category': category,
                    'cloud_provider': str(row.get('cloud_provider', 'All')),
                    'resource_scope': str(row.get('resource_scope', 'Global'))
                }
            vocab[key]['values'].append(value)
        
        return vocab
    
    def _decode_tag_columns(self) -> Dict[str, str]:
        """Decode Base64 tag column names"""
        decoder = {}
        for col in self.resources_df.columns:
            if col.startswith('tags.'):
                enc = col.replace('tags.', '')
                try:
                    decoder[col] = base64.b64decode(enc).decode('utf-8')
                except:
                    decoder[col] = enc
        return decoder
    
    def extract_features(self, row: pd.Series) -> Dict:
        """
        Extract ML features from a resource row.
        """
        name = str(row.get('name', '')) if pd.notna(row.get('name')) else ''
        
        features = {
            # Raw features
            'name': name,
            'resource_type': str(row.get('resource_type', '')) if pd.notna(row.get('resource_type')) else '',
            'service_name': str(row.get('service_name', '')) if pd.notna(row.get('service_name')) else '',
            'region': str(row.get('region', '')) if pd.notna(row.get('region')) else '',
            'cloud_resource_id': str(row.get('cloud_resource_id', ''))[:50],
            
            # Derived features from name
            'name_has_prod': 1 if re.search(r'prod|prd|production', name.lower()) else 0,
            'name_has_dev': 1 if re.search(r'dev|development', name.lower()) else 0,
            'name_has_staging': 1 if re.search(r'stag|staging|stg', name.lower()) else 0,
            'name_has_test': 1 if re.search(r'test|testing|qa', name.lower()) else 0,
            'name_has_api': 1 if re.search(r'api|gateway|rest', name.lower()) else 0,
            'name_has_ml': 1 if re.search(r'ml|model|ai|sagemaker', name.lower()) else 0,
            'name_has_data': 1 if re.search(r'data|pipeline|etl|analytics', name.lower()) else 0,
            'name_length': len(name),
            'name_word_count': len(name.split('-')) if name else 0,
        }
        
        return features
    
    def extract_labels(self, row: pd.Series) -> Dict[str, str]:
        """
        Extract labels from native tags in the row.
        Maps native tag keys to schema tag keys.
        """
        labels = {}
        
        # Native key to schema key mapping
        key_mapping = {
            'Env': 'Environment',
            'STAGE': 'Environment',
            'PROD': 'Environment',
            'TEST': 'Environment',
            'Project': 'Project',
            'CreatedBy': 'Owner',
            'Project Owner': 'Owner',
            'RetentionDays': 'RetentionDays',
            'name': 'Name',
        }
        
        # Value normalization
        value_norm = {
            'prod': 'prod', 'production': 'prod', 'PROD': 'prod',
            'dev': 'dev', 'development': 'dev', 'DEV': 'dev',
            'staging': 'staging', 'stag': 'staging', 'STAGE': 'staging',
            'test': 'testing', 'testing': 'testing', 'TEST': 'testing',
        }
        
        for col, native_key in self.tag_decoder.items():
            value = row.get(col)
            if pd.notna(value) and str(value).strip():
                value = str(value).strip()
                
                # Map to schema key
                schema_key = key_mapping.get(native_key, native_key)
                
                # Normalize value
                normalized_value = value_norm.get(value, value)
                
                # Only include if key exists in schema vocabulary
                if schema_key in self.tag_vocabulary:
                    labels[schema_key] = normalized_value
        
        return labels
    
    def generate_training_data(self, include_unlabeled: bool = False) -> pd.DataFrame:
        """
        Generate training data combining features and labels.
        
        Args:
            include_unlabeled: If True, include resources without native tags
        
        Returns:
            DataFrame with features and labels
        """
        data = []
        
        print("\nGenerating training data...")
        
        for idx, row in self.resources_df.iterrows():
            features = self.extract_features(row)
            labels = self.extract_labels(row)
            
            # Skip if no labels and not including unlabeled
            if not labels and not include_unlabeled:
                continue
            
            # Combine features and labels
            record = {**features}
            
            # Add label columns (prefixed with 'label_')
            for tag_key in self.tag_vocabulary.keys():
                record[f'label_{tag_key}'] = labels.get(tag_key, '')
            
            # Add metadata
            record['has_labels'] = 1 if labels else 0
            record['num_labels'] = len(labels)
            
            data.append(record)
            
            if (idx + 1) % 10000 == 0:
                print(f"  Processed {idx + 1} rows...")
        
        df = pd.DataFrame(data)
        print(f"\nGenerated {len(df)} training records")
        
        return df
    
    def generate_per_tag_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Generate separate training dataset for each tag key.
        Useful for training individual models per tag.
        """
        training_data = self.generate_training_data(include_unlabeled=False)
        
        datasets = {}
        feature_cols = [c for c in training_data.columns if not c.startswith('label_') and c not in ['has_labels', 'num_labels']]
        
        for tag_key in self.tag_vocabulary.keys():
            label_col = f'label_{tag_key}'
            
            # Filter to rows where this label exists
            mask = training_data[label_col] != ''
            if mask.sum() > 0:
                df = training_data.loc[mask, feature_cols + [label_col]].copy()
                df = df.rename(columns={label_col: 'label'})
                datasets[tag_key] = df
                print(f"  {tag_key}: {len(df)} samples")
        
        return datasets
    
    def generate_llm_training_data(self) -> List[Dict]:
        """
        Generate training data in LLM fine-tuning format.
        Format: {"prompt": "...", "completion": "..."}
        """
        training_data = self.generate_training_data(include_unlabeled=False)
        
        llm_data = []
        
        for _, row in training_data.iterrows():
            # Build prompt
            prompt = f"""Given a cloud resource with:
- Name: {row['name']}
- Resource Type: {row['resource_type']}
- Service: {row['service_name']}
- Region: {row['region']}

Predict the appropriate virtual tags from the allowed values:
{json.dumps({k: v['values'] for k, v in self.tag_vocabulary.items()}, indent=2)}

Response format: {{"tag_key": "predicted_value", ...}}"""

            # Build completion (ground truth)
            labels = {}
            for tag_key in self.tag_vocabulary.keys():
                val = row.get(f'label_{tag_key}', '')
                if val:
                    labels[tag_key] = val
            
            if labels:
                completion = json.dumps(labels)
                llm_data.append({
                    'prompt': prompt,
                    'completion': completion,
                    'resource_name': row['name'],
                    'resource_type': row['resource_type']
                })
        
        print(f"\nGenerated {len(llm_data)} LLM training samples")
        return llm_data
    
    def export_vocabulary(self, filepath: str):
        """Export schema vocabulary as JSON for model constraints"""
        with open(filepath, 'w') as f:
            json.dump(self.tag_vocabulary, f, indent=2)
        print(f"Vocabulary exported to {filepath}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about the training data"""
        labeled_count = 0
        label_distribution = defaultdict(lambda: defaultdict(int))
        
        for _, row in self.resources_df.iterrows():
            labels = self.extract_labels(row)
            if labels:
                labeled_count += 1
                for key, value in labels.items():
                    label_distribution[key][value] += 1
        
        return {
            'total_resources': len(self.resources_df),
            'labeled_resources': labeled_count,
            'labeled_percentage': labeled_count / len(self.resources_df) * 100,
            'label_distribution': dict(label_distribution),
            'schema_tags': list(self.tag_vocabulary.keys()),
            'schema_tag_count': len(self.tag_vocabulary)
        }


def main():
    print("=" * 60)
    print("ML Training Data Generator")
    print("=" * 60)
    
    # Initialize generator
    generator = MLTrainingDataGenerator(
        schema_path='cloud_resource_tags_complete 1.xlsx',
        resources_path='restapi.resources (1).xlsx'
    )
    
    # Get statistics
    print("\n" + "=" * 60)
    print("DATA STATISTICS")
    print("=" * 60)
    stats = generator.get_statistics()
    print(f"Total resources: {stats['total_resources']:,}")
    print(f"Resources with labels: {stats['labeled_resources']:,} ({stats['labeled_percentage']:.2f}%)")
    print(f"Schema tags: {stats['schema_tag_count']}")
    
    print("\nLabel distribution:")
    for tag_key, values in stats['label_distribution'].items():
        print(f"\n  {tag_key}:")
        for val, count in sorted(values.items(), key=lambda x: -x[1])[:5]:
            print(f"    {val}: {count}")
    
    # Generate main training data
    print("\n" + "=" * 60)
    print("GENERATING TRAINING DATA")
    print("=" * 60)
    
    training_df = generator.generate_training_data(include_unlabeled=False)
    training_df.to_csv('ml_training_data.csv', index=False)
    print(f"Saved: ml_training_data.csv ({len(training_df)} rows)")
    
    # Generate per-tag datasets
    print("\nPer-tag datasets:")
    per_tag = generator.generate_per_tag_datasets()
    for tag_key, df in per_tag.items():
        filename = f'ml_training_{tag_key.lower()}.csv'
        df.to_csv(filename, index=False)
    
    # Generate LLM format
    llm_data = generator.generate_llm_training_data()
    with open('ml_training_llm.jsonl', 'w') as f:
        for item in llm_data:
            f.write(json.dumps(item) + '\n')
    print(f"Saved: ml_training_llm.jsonl ({len(llm_data)} samples)")
    
    # Export vocabulary
    generator.export_vocabulary('ml_tag_vocabulary.json')
    
    print("\n" + "=" * 60)
    print("OUTPUT FILES")
    print("=" * 60)
    print("  ml_training_data.csv       - Main training dataset")
    print("  ml_training_*.csv          - Per-tag-key datasets")
    print("  ml_training_llm.jsonl      - LLM fine-tuning format")
    print("  ml_tag_vocabulary.json     - Valid tag values (for constrained decoding)")


if __name__ == '__main__':
    main()
