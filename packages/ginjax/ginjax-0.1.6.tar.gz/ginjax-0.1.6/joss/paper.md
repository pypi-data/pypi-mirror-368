---
title: 'ginjax: E(d)-Equivariant CNN for Tensor Images'
tags:
  - Python
  - Jax
  - machine learning
  - E(d)-equivariance
  - tensor images
  - Equinox
authors:
  - name: Wilson G. Gregory
    orcid: 0000-0002-5511-0683
    corresponding: true
    affiliation: 1 
  - name: Kaze W. K. Wong
    orcid: 0000-0001-8432-7788
    affiliation: 1
  - name: David W. Hogg
    orcid: 0000-0003-2866-9403
    affiliation: "2, 3, 4"
  - name: Soledad Villar
    orcid: 0000-0003-4968-3829
    affiliation: "1, 5, 6"
  
affiliations:
 - name: Department of Applied Mathematics and Statistics, Johns Hopkins University, Baltimore, MD, United States
   index: 1
 - name: Center for Cosmology and Particle Physics, Department of Physics, New York University, New York, NY, United States
   index: 2
 - name: Max-Planck-Institut f\"ur Astronomie, Heidelberg, Germany
   index: 3
 - name: Center for Computational Astrophysics, Flatiron Institute, New York, NY, United States
   index: 4
 - name: Center for Computational Mathematics, Flatiron Institute, New York, NY, United States
   index: 5
 - name: Mathematical Institute for Data Science, Johns Hopkins University, Baltimore, MD, United States
   index: 6
 
date: 25 March 2025
bibliography: paper.bib
---

# Summary

Many data sets encountered in machine learning exhibit symmetries that can be exploited to improve performance, a technique known as equivariant machine learning. 
The classical example is image translation equivariance that is respected by convolutional neural networks [@lecun1989backpropagation]. 
For data sets in the physical sciences and other areas, we would also like equivariance to rotations and reflections. 
This Python package implements a convolutional neural network that is equivariant to translations, rotations of 90 degrees, and reflections. 
We implement this by _geometric convolutions_ [@gregory2024ginet] which use tensor products and tensor contractions. 
This additionally enables us to perform functions on geometric images, or images where each pixel is a higher order tensor. 
These images appear as discretizations of fields in physics, such as velocity fields, vorticity fields, magnetic fields, polarization fields, and so on. 

The key features and use cases are summarized below.

## Key Features

1. Create, visualize and perform mathematical operations on geometric images, including powerful `jax` [@jax2018github] features such as vmap.
2. Combine geometric images of any tensor order or parity into a single `MultiImage` data structure.
3. Build `equinox` [@kidger2021equinox] neural networks with our custom equivariant layers that process `MultiImages`.
4. _Or_, use one of our off-the-shelf models (UNet, ResNet, etc.) to start processing your geometric image datasets right away.

# Statement of need

The geometric convolutions introduced in [@gregory2024ginet] are defined on geometric images – images where every pixel is a tensor.
If $A$ is a geometric image of tensor order $k$ and $C$ is a geometric image of tensor order $k'$, then the value of $A$ convolved with $C$ at pixel $\bar\imath$ is given by:

$$
(A \ast C)(\bar\imath) = \sum_{\bar a} A(\bar\imath - \bar a) \otimes C(\bar a) ~,
$$

where the sum is over all pixels $\bar a$ of $C$, and $\bar\imath - \bar a$ is the translation of $\bar\imath$ by $\bar a$. 
The result is a geometric image of tensor order $k+k'$. 
To produce geometric images of smaller tensor order, a tensor contraction can be applied to each pixel. 
Convolution and contraction are combined into a single operation to form linear layers. 
By restricting the convolution filters $C$ to rotation and reflection invariant filters, we can create linear layers which are rotation-, reflection-, and translation-equivariant.

ginjax has two main target audiences:

## For machine learning practitioners

The ginjax package can be used as a drop-in replacement for CNNs with minimal code changes required.
We define equivariant versions for all the common CNN operations including convolutions, activation functions, group norms, pooling, and unpooling.
Each of these layers require keeping track of the tensor order and parity of each geometric image, so we define a special data structure, the `MultiImage`, for these equivariant layers to operate on.
We can then easily turn a non-equivariant CNN into an equivariant CNN by replacing the layers and converting the input to a `MultiImage`.
We also provide full-fledged model implementations such as the UNet, ResNet, and Dilated ResNet.

This package is the only one implementing geometric convolutions, but there are alternative methods for solving $O(d)$-equivariant image problems.
One such package is [escnn](https://github.com/QUVA-Lab/escnn) which uses Steerable CNNs [@cohen2016steerablecnns;@weiler2021steerable].
Steerable CNNs use irreducible representations to derive a basis for $O(d)$-equivariant layers, but it is not straightforward to apply on higher-order tensor images.

Other alternative methods are those based on Clifford Algebras, in particular [@brandstetter2023clifford].
This method has been implemented in the [Clifford Layers](https://github.com/microsoft/cliffordlayers) package.
Clifford based methods can process vectors and pseudovectors, but cannot handle higher-order tensors.
Additionally, both these methods are built with pytorch, rather than `jax`.

## For equivariance researchers
To allow researchers to explore the behavior of geometric images, we implement all the common operations such as addition, scaling, convolution, contraction, transposition, norms, rotations, and reflections.
This makes it easy to generate group-invariant images and experiment with equivariant functions.
We also provide visualization methods to easily follow along with the operations.

# References
