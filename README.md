CrediBoost - unmasking the influence of fake reviews on the market place along with it's impact 

<img width="906" alt="Screenshot 2025-05-10 at 5 51 47 PM" src="https://github.com/user-attachments/assets/987b5ecd-e5b5-4038-ad7c-1846af9897bd" />

We start by preprocessing the text to ensure consistency and remove noise for better model performance. The text is converted to lowercase and punctuation marks,special characters and whitespaces are removed.
To convert unstructured textual data into a structured numerical format, the Term Frequency-Inverse Document Frequency (TF-IDF) method is used.TF-IDF emphasizes terms that are important to a specific use case while penalizing those that are common across all use cases. This helps us attain the distinguishing features that are of significant importance during text classification.A fixed vocabulary size(5000) is chosen to reduce dimensionality and computational complexity.
The classification model is implemented using the PyTorch deep learning framework
A simple feed forward neural network is designed that consists of
i. Input layer: it consists of 5000 nodes accepts the TF-IDF vectors as the input
ii. Hidden layer: The model includes a single hidden layer comprising 768 neurons, utilizing the ReLU (Rectified Linear Unit) activation function.
iii. A dropout mechanism is applied during training to mitigate overfitting by randomly deactivating a fraction of neurons.
iv. Output layer: We use a single neuron with a sigmoid function to give us a score that shows how likely it is that a review is fake.
We train the model using Binary Cross Entropy Loss, which works for binary classification. For optimization, we use the Adam optimizer due to its adaptive learning rate and strong convergence performance
Training is conducted over multiple epochs, with the data processed in batches during each epoch. This batch-wise training approach enhances memory efficiency and contributes to more stable and consistent gradient updates throughout the learning process.
The model is trained on two distinct datasets, effectively functioning as two separate models. The first dataset comprises real and fake reviews from e-commerce websites. The second is a custom-built dataset containing AI-generated reviews with varied prompts alongside genuine reviews sourced from product pages on e-commerce platforms
Once trained, the model is used to classify new reviews in real-time. During which the same preprocessing and TF-IDF vectorization pipeline is applied to new input text to maintain consistency.
The label for each review is decided on the basis of the following:
If it is classified as fake from the first classifier → fake
If it is classified as real from the first classifier but fake from the second classifier → fake
Otherwise → real
To understand how fake reviews impact consumer engagement, we look at how the number of reviews changes within a particular window before and after each detected fake review.We calculate the percentage change in review frequency during this period.
Let
Cbefore = number of reviews x days before
Cafter = number of reviews x days after
Then
Percent change = ( (Cbefore - Cafter+1) / (Cafter+1)) * 100
Laplacian corrector applied for handling zero values
Aggregated statistics are computed like mean, median for all fake reviews left on the product that gives us the impact score.
Additionally, we also compute other statistics like fake reviews in the past month and week, percent change from previous months and weeks. This helps consumers make more informed decisions with respect to product purchasing
