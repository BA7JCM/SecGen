#!/usr/bin/ruby
require_relative '../../../../../lib/objects/local_hash_encoder.rb'
require 'sha3'

class SHA3_384_Encoder < HashEncoder
  def initialize
    super
    self.module_name = 'SHA3-384 Encoder'
  end

  def hash_function(string)
    SHA3::Digest.hexdigest(:sha384, string)
  end
end

SHA3_384_Encoder.new.run