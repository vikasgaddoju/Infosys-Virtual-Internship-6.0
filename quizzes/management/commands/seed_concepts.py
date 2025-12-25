# quizzes/management/commands/seed_concepts.py
"""
Django management command to seed concepts for all subcategories.
"""
from django.core.management.base import BaseCommand
from quizzes.models import SubCategory, Concept


class Command(BaseCommand):
    help = 'Seed the database with concepts for all leaf subcategories'

    def handle(self, *args, **options):
        self.stdout.write('Seeding concepts...')
        
        # Define concepts for each topic and difficulty
        CONCEPTS = {
            # CSE Topics
            'Java': {
                'easy': ['Variables', 'Data Types', 'Operators', 'Loops', 'Conditionals', 
                         'Arrays', 'Methods', 'Classes', 'Objects', 'Strings', 
                         'Input/Output', 'Basic Syntax'],
                'medium': ['Inheritance', 'Polymorphism', 'Encapsulation', 'Abstraction',
                           'Interfaces', 'Exception Handling', 'Collections', 'Generics',
                           'File I/O', 'Multithreading', 'Lambda Expressions', 'Streams'],
                'hard': ['JVM Internals', 'Memory Management', 'Garbage Collection', 
                         'Design Patterns', 'Concurrency', 'Reflection', 'Annotations',
                         'ClassLoaders', 'Serialization', 'Network Programming', 
                         'JDBC Advanced', 'Performance Tuning']
            },
            'Python': {
                'easy': ['Variables', 'Data Types', 'Operators', 'Strings', 'Lists',
                         'Tuples', 'Dictionaries', 'Sets', 'Loops', 'Conditionals',
                         'Functions', 'Basic Syntax'],
                'medium': ['List Comprehensions', 'Decorators', 'Generators', 'Lambda Functions',
                           'Exception Handling', 'File I/O', 'Modules', 'Packages',
                           'OOP Basics', 'Inheritance', 'Regular Expressions', 'JSON Handling'],
                'hard': ['Metaclasses', 'Context Managers', 'Async/Await', 'Coroutines',
                         'Memory Management', 'GIL', 'Descriptors', 'Magic Methods',
                         'Design Patterns', 'Concurrency', 'Multiprocessing', 'C Extensions']
            },
            'Operating Systems': {
                'easy': ['Process', 'Thread', 'CPU Scheduling', 'Memory', 'Files',
                         'Directories', 'Commands', 'Shell', 'Kernel', 'User Mode',
                         'System Calls', 'Booting'],
                'medium': ['Process Scheduling Algorithms', 'Deadlock', 'Semaphores', 'Mutex',
                           'Virtual Memory', 'Paging', 'Segmentation', 'File Systems',
                           'Disk Scheduling', 'Process Synchronization', 'IPC', 'Threads'],
                'hard': ['Page Replacement Algorithms', 'Memory Allocation Strategies', 
                         'Distributed Systems', 'Real-time OS', 'Security',
                         'Kernel Architecture', 'Device Drivers', 'Virtualization',
                         'Container Technologies', 'OS Internals', 'System Performance', 'RAID']
            },
            'Data Structures': {
                'easy': ['Arrays', 'Linked Lists', 'Stacks', 'Queues', 'Strings',
                         'Linear Search', 'Binary Search', 'Sorting Basics', 'Time Complexity',
                         'Space Complexity', 'Recursion Basics', 'Pointers'],
                'medium': ['Trees', 'Binary Trees', 'BST', 'Heaps', 'Hash Tables',
                           'Graphs Basics', 'BFS', 'DFS', 'Sorting Algorithms', 
                           'Merge Sort', 'Quick Sort', 'Dynamic Programming Basics'],
                'hard': ['AVL Trees', 'Red-Black Trees', 'B-Trees', 'Tries', 'Segment Trees',
                         'Fenwick Trees', 'Graph Algorithms', 'Dijkstra', 'Bellman-Ford',
                         'Floyd-Warshall', 'Advanced DP', 'NP-Complete Problems']
            },
            'DBMS': {
                'easy': ['Database', 'Tables', 'Rows', 'Columns', 'Primary Key',
                         'Foreign Key', 'SELECT', 'INSERT', 'UPDATE', 'DELETE',
                         'WHERE Clause', 'ORDER BY'],
                'medium': ['Normalization', 'Joins', 'Subqueries', 'Indexes', 'Views',
                           'Transactions', 'ACID Properties', 'ER Diagrams', 'Relationships',
                           'GROUP BY', 'HAVING', 'Aggregate Functions'],
                'hard': ['Query Optimization', 'Concurrency Control', 'Locking', 'MVCC',
                         'Distributed Databases', 'Sharding', 'Replication', 'CAP Theorem',
                         'NoSQL vs SQL', 'Database Tuning', 'Stored Procedures', 'Triggers']
            },
            # AIML Topics
            'Machine Learning': {
                'easy': ['Supervised Learning', 'Unsupervised Learning', 'Training Data',
                         'Test Data', 'Features', 'Labels', 'Classification', 'Regression',
                         'Overfitting', 'Underfitting', 'Accuracy', 'Model'],
                'medium': ['Decision Trees', 'Random Forest', 'SVM', 'K-Means', 'KNN',
                           'Linear Regression', 'Logistic Regression', 'Cross-Validation',
                           'Feature Engineering', 'Dimensionality Reduction', 'PCA', 'Ensemble Methods'],
                'hard': ['Gradient Boosting', 'XGBoost', 'Regularization', 'Hyperparameter Tuning',
                         'Bias-Variance Tradeoff', 'ROC-AUC', 'Precision-Recall', 'Model Deployment',
                         'MLOps', 'AutoML', 'Interpretability', 'Fairness in ML']
            },
            'Deep Learning': {
                'easy': ['Neural Network', 'Neuron', 'Activation Function', 'Weights', 'Bias',
                         'Forward Propagation', 'Loss Function', 'Epochs', 'Batch Size',
                         'Learning Rate', 'Training', 'Layers'],
                'medium': ['Backpropagation', 'Gradient Descent', 'CNN', 'RNN', 'LSTM',
                           'Dropout', 'Batch Normalization', 'Pooling', 'Convolution',
                           'Transfer Learning', 'Data Augmentation', 'Optimizers'],
                'hard': ['Transformers', 'Attention Mechanism', 'GANs', 'VAEs', 'BERT', 'GPT',
                         'ResNet', 'Object Detection', 'Semantic Segmentation', 'Neural Architecture Search',
                         'Quantization', 'Model Compression']
            },
            'Neural Networks': {
                'easy': ['Perceptron', 'Activation', 'Sigmoid', 'ReLU', 'Input Layer',
                         'Hidden Layer', 'Output Layer', 'Weights', 'Bias', 'Training',
                         'Feedforward', 'Loss'],
                'medium': ['Multilayer Perceptron', 'Backpropagation', 'Vanishing Gradient',
                           'Weight Initialization', 'Learning Rate Scheduling', 'Momentum',
                           'Adam Optimizer', 'Regularization', 'Early Stopping', 'Hyperparameters',
                           'Architecture Design', 'Softmax'],
                'hard': ['Skip Connections', 'Residual Networks', 'Attention Mechanisms',
                         'Self-Attention', 'Positional Encoding', 'Layer Normalization',
                         'Gradient Clipping', 'Neural Architecture Search', 'Pruning',
                         'Knowledge Distillation', 'Adversarial Training', 'Meta-Learning']
            },
            'NLP': {
                'easy': ['Text', 'Tokenization', 'Words', 'Sentences', 'Vocabulary',
                         'Stopwords', 'Stemming', 'Lemmatization', 'Bag of Words', 'TF-IDF',
                         'Corpus', 'N-grams'],
                'medium': ['Word Embeddings', 'Word2Vec', 'GloVe', 'Sentiment Analysis',
                           'Named Entity Recognition', 'POS Tagging', 'Text Classification',
                           'Sequence Labeling', 'Language Models', 'Perplexity', 'BLEU Score', 'RNNs for NLP'],
                'hard': ['Transformers', 'BERT', 'GPT', 'Attention Mechanism', 'Machine Translation',
                         'Question Answering', 'Text Generation', 'Summarization', 'Dialogue Systems',
                         'Zero-Shot Learning', 'Few-Shot Learning', 'Prompt Engineering']
            },
            # Medical Topics
            'Anatomy': {
                'easy': ['Bones', 'Muscles', 'Organs', 'Heart', 'Lungs', 'Brain',
                         'Skeleton', 'Joints', 'Tissues', 'Cells', 'Blood', 'Skin'],
                'medium': ['Cardiovascular System', 'Respiratory System', 'Nervous System',
                           'Digestive System', 'Muscular System', 'Skeletal System',
                           'Endocrine System', 'Lymphatic System', 'Urinary System',
                           'Reproductive System', 'Integumentary System', 'Sensory Organs'],
                'hard': ['Neuroanatomy', 'Histology', 'Embryology', 'Regional Anatomy',
                         'Cross-sectional Anatomy', 'Clinical Correlations', 'Vascular Supply',
                         'Nerve Distribution', 'Lymphatic Drainage', 'Surface Anatomy',
                         'Radiological Anatomy', 'Surgical Anatomy']
            },
            'Physiology': {
                'easy': ['Breathing', 'Heartbeat', 'Digestion', 'Blood Circulation', 'Reflexes',
                         'Body Temperature', 'Sleep', 'Hunger', 'Thirst', 'Pain',
                         'Movement', 'Senses'],
                'medium': ['Action Potential', 'Cardiac Cycle', 'Gas Exchange', 'Homeostasis',
                           'Hormone Regulation', 'Nerve Conduction', 'Muscle Contraction',
                           'Kidney Function', 'Acid-Base Balance', 'Blood Pressure Regulation',
                           'Immune Response', 'Metabolism'],
                'hard': ['Renal Physiology', 'Cardiac Electrophysiology', 'Neurophysiology',
                         'Endocrine Feedback', 'Respiratory Mechanics', 'GI Motility',
                         'Membrane Transport', 'Signal Transduction', 'Receptor Physiology',
                         'Exercise Physiology', 'Altitude Physiology', 'Clinical Correlations']
            },
            'Biochemistry': {
                'easy': ['Proteins', 'Carbohydrates', 'Lipids', 'Vitamins', 'Minerals',
                         'Water', 'Enzymes', 'DNA', 'RNA', 'Amino Acids', 'Glucose', 'ATP'],
                'medium': ['Glycolysis', 'Krebs Cycle', 'Electron Transport Chain', 'Protein Synthesis',
                           'DNA Replication', 'Transcription', 'Translation', 'Enzyme Kinetics',
                           'Metabolic Pathways', 'Hormone Biochemistry', 'Lipid Metabolism', 'Nitrogen Metabolism'],
                'hard': ['Molecular Biology', 'Gene Expression', 'Epigenetics', 'Signal Transduction',
                         'Metabolic Regulation', 'Clinical Biochemistry', 'Inborn Errors',
                         'Drug Metabolism', 'Free Radicals', 'Antioxidants', 'Proteomics', 'Genomics']
            },
            'Pharmacology': {
                'easy': ['Drugs', 'Dosage', 'Side Effects', 'Prescription', 'OTC Drugs',
                         'Antibiotics', 'Painkillers', 'Vaccines', 'Tablets', 'Injections',
                         'Drug Safety', 'Drug Names'],
                'medium': ['Pharmacokinetics', 'Pharmacodynamics', 'Drug Absorption', 'Distribution',
                           'Metabolism', 'Excretion', 'Drug Interactions', 'Receptor Theory',
                           'Dose-Response', 'Therapeutic Index', 'Drug Classes', 'Adverse Effects'],
                'hard': ['Clinical Pharmacology', 'Drug Development', 'Pharmacogenomics',
                         'Drug Resistance', 'Toxicology', 'Chemotherapy', 'Immunopharmacology',
                         'CNS Pharmacology', 'Cardiovascular Pharmacology', 'Antimicrobial Resistance',
                         'Drug Trials', 'Regulatory Affairs']
            },
            # Entertainment Topics
            'Movies': {
                'easy': ['Actors', 'Directors', 'Genres', 'Hollywood', 'Bollywood', 'Oscar',
                         'Box Office', 'Sequels', 'Remakes', 'Animation', 'Comedy', 'Drama'],
                'medium': ['Film History', 'Cinematography', 'Screenwriting', 'Film Genres',
                           'Award Shows', 'Film Studios', 'Iconic Movies', 'Film Techniques',
                           'Movie Franchises', 'Documentary', 'International Cinema', 'Film Industry'],
                'hard': ['Film Theory', 'Auteur Theory', 'Film Analysis', 'Film Movements',
                         'Noir Cinema', 'New Wave', 'Film Criticism', 'Experimental Film',
                         'Film Restoration', 'Silent Era', 'Film Technology', 'Cult Classics']
            },
            'Music': {
                'easy': ['Singers', 'Bands', 'Songs', 'Albums', 'Genres', 'Pop', 'Rock',
                         'Hip Hop', 'Classical', 'Instruments', 'Concerts', 'Grammy'],
                'medium': ['Music History', 'Music Theory Basics', 'Famous Musicians', 'Record Labels',
                           'Music Festivals', 'Album Production', 'Music Charts', 'Iconic Albums',
                           'Music Genres', 'Songwriting', 'Music Industry', 'Live Performances'],
                'hard': ['Music Theory Advanced', 'Composition', 'Orchestration', 'Music Analysis',
                         'Ethnomusicology', 'Music Technology', 'Sound Engineering', 'Music Criticism',
                         'Classical Periods', 'Jazz History', 'Electronic Music', 'Music Business']
            },
            'TV Shows': {
                'easy': ['Series', 'Episodes', 'Seasons', 'Sitcoms', 'Drama', 'Reality TV',
                         'Characters', 'Actors', 'Networks', 'Streaming', 'Emmy', 'Ratings'],
                'medium': ['TV History', 'Show Runners', 'TV Genres', 'Iconic Shows', 'TV Production',
                           'Spin-offs', 'Reboots', 'Streaming Wars', 'Binge Watching', 'TV Networks',
                           'International TV', 'TV Awards'],
                'hard': ['TV Criticism', 'Narrative Structure', 'TV Industry', 'Serialized Storytelling',
                         'TV Golden Age', 'Prestige TV', 'TV Production Process', 'Showrunning',
                         'TV Writing', 'TV Marketing', 'Audience Analytics', 'Platform Strategy']
            },
            'Gaming': {
                'easy': ['Video Games', 'Consoles', 'PC Gaming', 'Mobile Games', 'Genres',
                         'Characters', 'Multiplayer', 'Single Player', 'Controllers', 'Graphics',
                         'Game Studios', 'Popular Games'],
                'medium': ['Game Development', 'Game Engines', 'Esports', 'Gaming History',
                           'Game Franchises', 'Indie Games', 'VR Gaming', 'Game Design',
                           'Gaming Platforms', 'Online Gaming', 'Gaming Community', 'Game Awards'],
                'hard': ['Game Theory', 'Game Mechanics', 'Level Design', 'Game AI',
                         'Game Physics', 'Shader Programming', 'Game Monetization', 'Game Analytics',
                         'Gaming Industry', 'Game Preservation', 'Speedrunning', 'Competitive Gaming']
            },
            # General Knowledge Topics
            'History': {
                'easy': ['Ancient Civilizations', 'World Wars', 'Independence', 'Kings', 'Queens',
                         'Empires', 'Revolutions', 'Famous Leaders', 'Historical Events',
                         'Monuments', 'Timeline', 'Famous Battles'],
                'medium': ['Medieval History', 'Renaissance', 'Industrial Revolution', 'Cold War',
                           'Colonial Era', 'World History', 'Regional History', 'Historical Figures',
                           'Political History', 'Social Movements', 'Economic History', 'Military History'],
                'hard': ['Historiography', 'Historical Analysis', 'Primary Sources', 'Archaeological Evidence',
                         'Historical Debates', 'Comparative History', 'Cultural History', 'Intellectual History',
                         'Environmental History', 'Transnational History', 'Historical Methods', 'Historical Theory']
            },
            'Geography': {
                'easy': ['Countries', 'Capitals', 'Continents', 'Oceans', 'Rivers', 'Mountains',
                         'Deserts', 'Forests', 'Climate', 'Maps', 'Borders', 'Landmarks'],
                'medium': ['Physical Geography', 'Human Geography', 'Climate Zones', 'Plate Tectonics',
                           'Population', 'Urban Geography', 'Economic Geography', 'Environmental Geography',
                           'Geopolitics', 'Natural Resources', 'Regional Geography', 'Cartography'],
                'hard': ['Geomorphology', 'Climatology', 'Biogeography', 'GIS', 'Remote Sensing',
                         'Spatial Analysis', 'Urban Planning', 'Sustainable Development',
                         'Environmental Management', 'Geographic Theory', 'Quantitative Geography', 'Field Methods']
            },
            'Science': {
                'easy': ['Physics Basics', 'Chemistry Basics', 'Biology Basics', 'Space', 'Planets',
                         'Animals', 'Plants', 'Human Body', 'Energy', 'Matter', 'Elements', 'Experiments'],
                'medium': ['Scientific Method', 'Famous Scientists', 'Scientific Discoveries',
                           'Physics Laws', 'Chemical Reactions', 'Ecology', 'Genetics', 'Evolution',
                           'Astronomy', 'Earth Science', 'Environmental Science', 'Technology'],
                'hard': ['Quantum Physics', 'Relativity', 'Organic Chemistry', 'Molecular Biology',
                         'Astrophysics', 'Neuroscience', 'Climate Science', 'Nanotechnology',
                         'Biotechnology', 'Scientific Research', 'Scientific Ethics', 'Cutting-edge Science']
            },
            'Current Affairs': {
                'easy': ['News', 'Politics', 'Sports News', 'Entertainment News', 'Technology News',
                         'Weather', 'Economy Basics', 'Elections', 'Summits', 'Awards',
                         'Appointments', 'Events'],
                'medium': ['International Relations', 'Economic Trends', 'Political Analysis',
                           'Social Issues', 'Environmental News', 'Technology Trends', 'Global Events',
                           'Policy Changes', 'Trade', 'Defense', 'Health News', 'Education News'],
                'hard': ['Geopolitical Analysis', 'Economic Analysis', 'Foreign Policy',
                         'Constitutional Matters', 'International Law', 'Global Governance',
                         'Security Issues', 'Development Issues', 'Climate Policy', 'Tech Regulation',
                         'Global Health', 'Emerging Issues']
            },
            'Sports': {
                'easy': ['Cricket', 'Football', 'Basketball', 'Tennis', 'Olympics', 'World Cup',
                         'Players', 'Teams', 'Rules', 'Tournaments', 'Records', 'Stadiums'],
                'medium': ['Sports History', 'Famous Athletes', 'Championships', 'Sports Organizations',
                           'Sports Records', 'International Sports', 'Sports Events', 'Sports Awards',
                           'Olympic Games', 'World Championships', 'Sports Statistics', 'Sports Venues'],
                'hard': ['Sports Science', 'Sports Management', 'Sports Analytics', 'Sports Psychology',
                         'Sports Law', 'Sports Economics', 'Doping', 'Sports Medicine',
                         'Sports Technology', 'Athlete Development', 'Sports Governance', 'Sports History Analysis']
            }
        }
        
        created_count = 0
        
        for topic_name, difficulties in CONCEPTS.items():
            # Find subcategory
            try:
                subcategory = SubCategory.objects.get(name=topic_name)
            except SubCategory.DoesNotExist:
                self.stdout.write(f'  Skipping {topic_name} - not found')
                continue
            
            for difficulty, concepts in difficulties.items():
                for concept_name in concepts:
                    concept, created = Concept.objects.get_or_create(
                        subcategory=subcategory,
                        difficulty=difficulty,
                        name=concept_name
                    )
                    if created:
                        created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} concepts!')
        )
