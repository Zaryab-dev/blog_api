# CloudFront CDN for static assets and API caching

resource "aws_cloudfront_distribution" "blog_api" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Blog API CDN"
  price_class         = "PriceClass_100"
  
  origin {
    domain_name = var.app_runner_domain
    origin_id   = "app-runner"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # Static files caching
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    target_origin_id = "app-runner"
    
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    compress         = true
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl                = 86400
    default_ttl            = 604800
    max_ttl                = 31536000
    viewer_protocol_policy = "redirect-to-https"
  }
  
  # API caching (short TTL)
  default_cache_behavior {
    target_origin_id = "app-runner"
    
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    compress         = true
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Origin"]
      
      cookies {
        forward = "all"
      }
    }
    
    min_ttl                = 0
    default_ttl            = 60
    max_ttl                = 300
    viewer_protocol_policy = "redirect-to-https"
  }
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  viewer_certificate {
    cloudfront_default_certificate = true
  }
  
  tags = {
    Name        = "blog-api-cdn"
    Environment = var.environment
  }
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.blog_api.domain_name
}
